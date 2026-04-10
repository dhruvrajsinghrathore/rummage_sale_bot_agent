# 🔌 Eddie's Electronics Garage Sale

A command-line chat agent powered by a local LLM (via Ollama) that simulates an electronics garage sale. The AI seller (Eddie) manages inventory, negotiates prices, and processes transactions — all through LLM tool-calling.

## Features

- **Agentic Tool-Calling**: All sale logic orchestrated through LLM function-calling
- **Time-Aware Negotiation**: Eddie adjusts pricing strategy based on time remaining in the sale
- **Full Transaction Management**: Cash box tracking, change calculation, sale history
- **Session Persistence**: State saved to JSON — resume where you left off across sessions
- **Local & Free**: Runs on Ollama with Qwen2.5 — no API keys or costs
- **Rich CLI Interface**: Colorful, formatted terminal output

## Quick Start

### 1. Install Ollama

```bash
# macOS
brew install ollama
```

### 2. Pull the Model

```bash
ollama pull qwen2.5:14b
```

> Alternative: `ollama pull llama3.1:8b` (set `OLLAMA_MODEL=llama3.1:8b` in `.env`)

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python rummage_sale.py
```

## Configuration

Optionally create a `.env` file to override defaults:

```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:14b
```

## Architecture

```
rummage_sale.py  →  Main CLI entry point & chat loop
agent.py         →  LLM function-calling agent loop & system prompt
tools.py         →  6 tool functions (inventory, sales, cash box)
state.py         →  State persistence (load/save JSON)
config.py        →  Configuration constants
sale_state.json  →  Persisted sale state (auto-generated)
```

### Tool Functions

| Tool | Purpose |
|---|---|
| `get_sale_status` | Current time, urgency level, items remaining |
| `browse_inventory` | List unsold items (optional category filter) |
| `get_item_details` | Item details + hidden min price for negotiation |
| `make_sale` | Complete purchase, update inventory & cash box |
| `get_cash_box` | Cash box balance and revenue summary |
| `get_transaction_history` | All completed sales |

### Negotiation Strategy

The bot adapts its pricing based on the time of day:

- **8–11 AM** (Relaxed): Firm on prices, ~10% discount max
- **11 AM–2 PM** (Moderate): Flexible, ~20% discount
- **2–4 PM** (Urgent): Motivated seller, accepts above minimum
- **Last 30 min** (Closing Soon): Deep discounts, bundle deals

> If run outside sale hours (8 AM–4 PM), the bot assumes it's 3 PM.

## Inventory

15 electronics items including vintage audio gear, gaming devices, gadgets, and accessories. Starting cash box: $150.

## Persistence

All state is saved to `sale_state.json` after every transaction:
- Inventory (with sold/unsold status)
- Cash box balance
- Transaction history

Delete `sale_state.json` to reset the sale.

## Design Decisions

1. **Raw SDK over frameworks**: Uses the OpenAI-compatible API directly instead of LangChain/CrewAI to demonstrate understanding of tool-calling fundamentals
2. **LLM as orchestrator**: The bot decides pricing strategy — code only provides tools, not business logic
3. **Hidden minimum prices**: The LLM knows each item's floor price but is instructed never to reveal it
4. **Multi-tool execution**: The agent loop handles multiple tool calls per turn for bundle purchases
5. **Local-first**: No external API keys needed — runs entirely on Ollama
