# Rummage Sale Agent — Design & Implementation Report

## Architecture & Design Choices

### Tech Stack Decisions

**Raw SDK over LangChain / CrewAI**
Using the raw OpenAI-compatible SDK provides full visibility into every tool definition, loop iteration, and result without unnecessary abstraction layers. Frameworks like LangChain or CrewAI were evaluated but deemed unnecessary overhead for a single-agent, deterministic-tool architecture. The raw SDK ensures clean, debuggable, and maintainable code.

**ReAct Agent Pattern**
The ReAct (Reason + Act) loop was chosen over a hardcoded state machine. The seller agent needs to reason about time, item specs, and secret floor prices before taking action. The ReAct architecture natively mirrors this decision-making cycle, creating immense conversational flexibility.

**Local Model (Qwen2.5:14b via Ollama)**
Running a local model guarantees zero API costs and total data privacy. Qwen2.5:14b was selected due to its superior and highly reliable structured JSON tool-calling capabilities compared to other similarly-sized open-source models, which is critical since every sale decision routes through system functions.

**JSON State Persistence**
A simple JSON file (`sale_state.json`) was used for state management. It is human-readable, requires zero configuration, and effectively maintains inventory and cash-box tracking across sessions for this single-user application.

### Core Mechanics
- **Decoupling Math from LLM Logic:** Large Language Models notoriously struggle with arithmetic and strict rule adherence. Validation logic is handled entirely by the Python backend. The LLM merely extracts intent (e.g., `make_sale(item_ids, sale_price, payment_amount)`), while Python handles the cash box math, validation, and change calculations.
- **Dynamic Prompt Injection:** To enforce strict business rules over long conversations, the sale's urgency state is dynamically evaluated by the backend and injected strictly into the LLM's system prompt on *every turn*. Urgency is implemented as a rigid mathematical constraint (e.g., "Accept any offer above 70%"), preventing the LLM from going off-script. Strict anti-jailbreak rules prevent the agent from leaking these constraints or secret floor prices.

---

## Technical Trade-offs

**1. Model Context Drift vs. Dynamic Injection**
Locally hosted models can experience instruction drift during lengthy negotiations. To counteract the model forgetting its urgency state or floor price secrecy, conversational state constraints are re-injected dynamically every single turn. This model limitation also directly influenced the architectural decision to offload all arithmetic to Python tool executors — a smaller local model is simply not reliable enough for cash calculations, change computation, or floor price validation, so Python owns all math entirely. This defensive engineering guarantees behavioral consistency regardless of the conversation length.

**2. State Concurrency**
JSON is fast and inspectable, but lacks row-level locking. For a single-user CLI application, this trade-off is optimal. For an online production environment with concurrent users, this state layer would require migration to SQLite or Redis to prevent overlapping sale race conditions.

---

## Future Scalability Paths

**1. Observability (Langfuse Integration)**
In production systems, tracking tool execution paths is critical. Integrating an observability platform like Langfuse would provide full traces of every agent turn (User Input → Model Reasoning → Tool Executed → Response), allowing auditing of negotiation performance, edge-case debugging, and latency monitoring.

**2. Vector DB for Large-Scale Inventory**
Passing the full inventory natively to the LLM works for a boutique garage sale, but scales poorly. To support catalogues of 10,000+ items, integrating a Vector Database (like ChromaDB or Pinecone) would allow the agent to semantic-search the inventory dynamically to preserve the context window.

**3. Algorithmic Pricing Engines**
Instead of static JSON-defined floor prices, a production iteration could integrate real-time market engines pulling data from sources like eBay to algorithmically set moving floor-price thresholds based on actual supply and demand.

**4. Concurrent Session Management**
The current JSON state file has no locking mechanism. For a single-user CLI demo this is a non-issue, but in a production environment with multiple simultaneous buyers, two users could theoretically purchase the same item creating a race condition. The migration path is straightforward — replace the JSON file with SQLite for small-scale concurrency using row-level locking, or Redis with atomic operations for high-throughput scenarios. The tool interface (`make_sale`, `browse_inventory`) would not change — only the persistence layer underneath would be swapped out.
