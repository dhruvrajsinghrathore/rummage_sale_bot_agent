"""
State management for the Rummage Sale agent.
Handles loading, saving, and initializing the sale state from/to a JSON file.
"""

import json
import os
from config import STATE_FILE, STARTING_CASH


def get_default_state() -> dict:
    """Returns the initial sale state with full electronics inventory."""
    return {
        "inventory": [
            {
                "id": "item_01",
                "name": "Sony Walkman WM-F2015",
                "category": "Audio",
                "description": "Classic portable cassette player from the 90s, fully working condition. Includes original foam headphones. A real collector's piece!",
                "original_price": 35.00,
                "min_price": 15.00,
                "sold": False
            },
            {
                "id": "item_02",
                "name": "Nintendo Game Boy Color (Teal)",
                "category": "Gaming",
                "description": "Teal Game Boy Color in great shape, minor screen scratches. Comes with Tetris cartridge. Hours of retro fun!",
                "original_price": 45.00,
                "min_price": 25.00,
                "sold": False
            },
            {
                "id": "item_03",
                "name": "Panasonic RX-5050 Boombox",
                "category": "Audio",
                "description": "Vintage dual-cassette boombox with AM/FM radio. Big sound, works perfectly. Great for the backyard or garage.",
                "original_price": 60.00,
                "min_price": 30.00,
                "sold": False
            },
            {
                "id": "item_04",
                "name": "Texas Instruments TI-84 Plus Calculator",
                "category": "Gadgets",
                "description": "Graphing calculator, perfect for students. Lightly used, all buttons responsive. Includes USB cable.",
                "original_price": 40.00,
                "min_price": 20.00,
                "sold": False
            },
            {
                "id": "item_05",
                "name": "Canon PowerShot A590 IS Digital Camera",
                "category": "Camera",
                "description": "8MP digital camera with 4x optical zoom and image stabilization. Takes AA batteries — super convenient. Comes with 2GB SD card.",
                "original_price": 25.00,
                "min_price": 10.00,
                "sold": False
            },
            {
                "id": "item_06",
                "name": "Apple iPod Nano 3rd Gen (8GB, Red)",
                "category": "Audio",
                "description": "Product RED iPod Nano, 8GB storage. Screen is clean, battery holds about 6 hours. Includes dock connector cable.",
                "original_price": 30.00,
                "min_price": 12.00,
                "sold": False
            },
            {
                "id": "item_07",
                "name": "Samsung 32\" LCD TV (no remote)",
                "category": "TV",
                "description": "32-inch Samsung LCD TV, 720p. Picture is great, all ports work. No remote but has buttons on the side. HDMI and component inputs.",
                "original_price": 50.00,
                "min_price": 20.00,
                "sold": False
            },
            {
                "id": "item_08",
                "name": "Logitech Z-2300 2.1 Speaker System",
                "category": "Audio",
                "description": "Legendary THX-certified 2.1 speaker system with subwoofer. 200W total power. The bass on this thing is insane!",
                "original_price": 55.00,
                "min_price": 25.00,
                "sold": False
            },
            {
                "id": "item_09",
                "name": "Dell Wireless Keyboard & Mouse Combo",
                "category": "Accessories",
                "description": "Wireless keyboard and mouse set with USB receiver. Full-size keyboard, comfortable mouse. Batteries included.",
                "original_price": 15.00,
                "min_price": 5.00,
                "sold": False
            },
            {
                "id": "item_10",
                "name": "Roku Express Streaming Stick",
                "category": "Streaming",
                "description": "Roku Express with remote and HDMI cable. Perfect for turning any TV into a smart TV. Easy setup.",
                "original_price": 20.00,
                "min_price": 8.00,
                "sold": False
            },
            {
                "id": "item_11",
                "name": "Garmin eTrex 20x Handheld GPS",
                "category": "Gadgets",
                "description": "Rugged handheld GPS with color screen and preloaded maps. Perfect for hiking and geocaching. Waterproof.",
                "original_price": 70.00,
                "min_price": 35.00,
                "sold": False
            },
            {
                "id": "item_12",
                "name": "Brother HL-L2300D Laser Printer",
                "category": "Office",
                "description": "Compact mono laser printer with duplex printing. About half toner remaining. Prints crisp text fast.",
                "original_price": 40.00,
                "min_price": 15.00,
                "sold": False
            },
            {
                "id": "item_13",
                "name": "Belkin 8-Outlet Surge Protector (2-pack)",
                "category": "Accessories",
                "description": "Two Belkin surge protectors with 6-foot cords. 8 outlets each. Great for home office or entertainment center.",
                "original_price": 12.00,
                "min_price": 5.00,
                "sold": False
            },
            {
                "id": "item_14",
                "name": "JBL Flip 3 Bluetooth Speaker (Blue)",
                "category": "Audio",
                "description": "Portable Bluetooth speaker, splashproof. Great sound for its size. Battery lasts about 8 hours. Charges via micro-USB.",
                "original_price": 35.00,
                "min_price": 15.00,
                "sold": False
            },
            {
                "id": "item_15",
                "name": "Fitbit Charge 2 Fitness Tracker",
                "category": "Wearable",
                "description": "Fitness tracker with heart rate monitor, step counter, and sleep tracking. Small/Medium band. Charger included.",
                "original_price": 28.00,
                "min_price": 10.00,
                "sold": False
            }
        ],
        "cash_box": STARTING_CASH,
        "transactions": []
    }


def load_state() -> dict:
    """Load state from JSON file, or create default state if file doesn't exist."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
            return state
        except (json.JSONDecodeError, IOError):
            # Corrupted file — start fresh
            state = get_default_state()
            save_state(state)
            return state
    else:
        state = get_default_state()
        save_state(state)
        return state


def save_state(state: dict) -> None:
    """Persist state to JSON file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
