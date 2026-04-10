"""
Configuration constants and environment setup for the Rummage Sale agent.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Ollama / LLM Configuration ---
# Ollama exposes an OpenAI-compatible API at this base URL
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")

# --- Sale Hours ---
SALE_START_HOUR = 8   # 8 AM
SALE_END_HOUR = 16    # 4 PM
DEFAULT_HOUR = 15     # 3 PM (used when outside sale hours)

# --- State File ---
STATE_FILE = "sale_state.json"

# --- Starting Cash Box ---
STARTING_CASH = 150.00
