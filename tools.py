"""
Tool functions for the Rummage Sale agent.
Each function operates on the state dict and returns a result dict for the LLM.
"""

from datetime import datetime
from config import SALE_START_HOUR, SALE_END_HOUR, DEFAULT_HOUR
from state import save_state


def get_sale_status(state: dict) -> dict:
    """
    Returns current sale time status, time remaining, and urgency level.
    If outside sale hours (8 AM - 4 PM), assumes 3 PM.
    """
    now = datetime.now()
    # Check for test override
    import os
    mock_hour = os.getenv("MOCK_TIME_HOUR")
    if mock_hour is not None:
        current_hour = int(mock_hour)
        current_minute = 0
    else:
        current_hour = now.hour
        current_minute = now.minute

    # Check if within sale hours
    if current_hour < SALE_START_HOUR or current_hour >= SALE_END_HOUR:
        # Outside sale hours — assume 3 PM
        effective_hour = DEFAULT_HOUR
        effective_minute = 0
        outside_hours = True
    else:
        effective_hour = current_hour
        effective_minute = current_minute
        outside_hours = False

    # Calculate minutes remaining until 4 PM
    minutes_remaining = (SALE_END_HOUR * 60) - (effective_hour * 60 + effective_minute)

    # Determine urgency level
    if minutes_remaining <= 30:
        urgency = "closing_soon"
        urgency_description = "CLOSING SOON — You MUST accept any offer at or above 50% of asking price. Start every response by mentioning the sale ends soon. Offer bundle deals unprompted."
    elif minutes_remaining <= 120:  # Last 2 hours (2 PM - 4 PM)
        urgency = "urgent"
        urgency_description = "URGENT — Accept any offer above 70% of asking price immediately. Do not counter more than once. Show visible eagerness to sell."
    elif minutes_remaining <= 300:  # 11 AM - 2 PM
        urgency = "moderate"
        urgency_description = "MODERATE — Accept offers within 80% of asking price. You may counter once but stay flexible."
    else:  # 8 AM - 11 AM
        urgency = "relaxed"
        urgency_description = "RELAXED — Hold firm. Only accept offers within 90% of asking price. You may reject low offers politely."

    # Count inventory stats
    total_items = len(state["inventory"])
    sold_items = sum(1 for item in state["inventory"] if item["sold"])
    unsold_items = total_items - sold_items

    return {
        "current_time": f"{effective_hour}:{effective_minute:02d}",
        "sale_hours": f"{SALE_START_HOUR}:00 AM - {SALE_END_HOUR - 12}:00 PM",
        "minutes_remaining": minutes_remaining,
        "urgency": urgency,
        "urgency_description": urgency_description,
        "outside_sale_hours": outside_hours,
        "note_if_outside": "The current time is outside sale hours, so we're simulating 3:00 PM." if outside_hours else None,
        "items_remaining": unsold_items,
        "items_sold": sold_items,
        "total_items": total_items
    }


def browse_inventory(state: dict, category: str = None) -> dict:
    """
    Returns all unsold items. Optionally filter by category.
    """
    unsold = [
        {
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "price": f"${item['original_price']:.2f}"
        }
        for item in state["inventory"]
        if not item["sold"] and (category is None or item["category"].lower() == category.lower())
    ]

    if not unsold:
        if category:
            return {
                "items": [],
                "message": f"No unsold items in the '{category}' category.",
                "total_unsold": sum(1 for item in state["inventory"] if not item["sold"])
            }
        return {
            "items": [],
            "message": "All items have been sold! The sale is over."
        }

    categories = sorted(set(item["category"] for item in unsold))
    return {
        "items": unsold,
        "count": len(unsold),
        "categories_available": categories
    }


def get_item_details(state: dict, item_id: str) -> dict:
    """
    Returns full details for a specific item, including min_price for negotiation.
    """
    for item in state["inventory"]:
        if item["id"] == item_id:
            if item["sold"]:
                return {
                    "error": f"Item '{item['name']}' has already been sold.",
                    "item_id": item_id,
                    "sold": True
                }
            return {
                "id": item["id"],
                "name": item["name"],
                "category": item["category"],
                "description": item["description"],
                "sticker_price_shown_to_buyer": item["original_price"],
                "SECRET_floor_price_DO_NOT_REVEAL": item["min_price"],
                "IMPORTANT_NOTE": (
                    "sticker_price_shown_to_buyer is what you tell the buyer. "
                    "SECRET_floor_price_DO_NOT_REVEAL is YOUR secret minimum — "
                    "NEVER say this number or hint at it. "
                    "You can accept any offer >= SECRET_floor_price. "
                    "These two prices are DIFFERENT numbers. Do not confuse them."
                )
            }

    return {"error": f"No item found with ID '{item_id}'."}


def make_sale(state: dict, item_ids: list, sale_price: float, payment_amount: float) -> dict:
    """
    Completes a sale for one or more items: validates, updates inventory, cash box, and logs transaction.
    """
    items = []
    # Find all items
    for i_id in item_ids:
        found = False
        for inv_item in state["inventory"]:
            if inv_item["id"] == i_id:
                items.append(inv_item)
                found = True
                break
        if not found:
            return {"error": f"No item found with ID '{i_id}'."}

    for item in items:
        if item["sold"]:
            return {"error": f"Item '{item['name']}' has already been sold. Cannot sell again."}

    # Validate sale price
    if sale_price <= 0:
        return {"error": "Sale price must be greater than $0."}

    min_total = sum(item["min_price"] for item in items)
    if sale_price < min_total:
        return {
            "error": f"Total sale price ${sale_price:.2f} is below the combined minimum acceptable price. Cannot complete this sale.",
            "min_acceptable_price_total": min_total
        }

    # Validate payment
    if payment_amount < sale_price:
        return {
            "error": f"Payment ${payment_amount:.2f} is less than the sale price ${sale_price:.2f}. Need at least ${sale_price:.2f}."
        }

    # Calculate change
    change = round(payment_amount - sale_price, 2)

    # Check if cash box has enough for change
    if change > 0 and state["cash_box"] < change:
        return {
            "error": f"Not enough cash in the box to make ${change:.2f} in change. Cash box has ${state['cash_box']:.2f}. Ask the buyer for closer to exact change."
        }

    # --- Execute the sale ---
    # Mark items as sold
    for item in items:
        item["sold"] = True

    # Update cash box: add payment, subtract change
    state["cash_box"] = round(state["cash_box"] + payment_amount - change, 2)

    # Log transaction
    item_names = [item["name"] for item in items]
    original_price_total = sum(item["original_price"] for item in items)
    
    transaction = {
        "item_id": ", ".join(item_ids),
        "item_name": " + ".join(item_names),
        "original_price": original_price_total,
        "sold_price": sale_price,
        "payment_amount": payment_amount,
        "change_given": change,
        "timestamp": datetime.now().isoformat(),
        "is_bundle": len(items) > 1
    }
    state["transactions"].append(transaction)

    # Persist state
    save_state(state)

    bundle_name = " + ".join(item_names)
    return {
        "success": True,
        "message": f"Sale complete! '{bundle_name}' sold for ${sale_price:.2f}.",
        "sale_price": sale_price,
        "payment_received": payment_amount,
        "change_given": change,
        "cash_box_balance": state["cash_box"],
        "items_remaining": sum(1 for i in state["inventory"] if not i["sold"])
    }


def get_cash_box(state: dict) -> dict:
    """
    Returns current cash box balance and revenue summary.
    """
    total_revenue = sum(t["sold_price"] for t in state["transactions"])
    total_transactions = len(state["transactions"])

    return {
        "current_balance": state["cash_box"],
        "starting_balance": 150.00,
        "total_revenue": round(total_revenue, 2),
        "total_transactions": total_transactions
    }


def get_transaction_history(state: dict) -> dict:
    """
    Returns all completed transactions.
    """
    if not state["transactions"]:
        return {
            "transactions": [],
            "message": "No sales have been made yet today."
        }

    return {
        "transactions": state["transactions"],
        "total_sales": len(state["transactions"]),
        "total_revenue": round(sum(t["sold_price"] for t in state["transactions"]), 2)
    }


# --- Tool dispatcher: maps tool names to functions ---
TOOL_FUNCTIONS = {
    "get_sale_status": lambda state, **kwargs: get_sale_status(state),
    "browse_inventory": lambda state, **kwargs: browse_inventory(state, category=kwargs.get("category")),
    "get_item_details": lambda state, **kwargs: get_item_details(state, item_id=kwargs["item_id"]),
    "make_sale": lambda state, **kwargs: make_sale(
        state,
        item_ids=kwargs["item_ids"],
        sale_price=float(kwargs["sale_price"]),
        payment_amount=float(kwargs["payment_amount"])
    ),
    "get_cash_box": lambda state, **kwargs: get_cash_box(state),
    "get_transaction_history": lambda state, **kwargs: get_transaction_history(state),
}
