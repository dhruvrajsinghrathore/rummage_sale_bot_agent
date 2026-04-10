# Requirements & Approach Summary

This document provides a high-level breakdown of the original project requirements and the conceptual design approach used to solve them. It focuses on *how* we thought about the problem and designed the architecture, rather than the raw code mechanics.

---

## 1. Time-Based Urgency
**The Requirement:** 
The garage sale runs from 8 AM to 4 PM. As the day progresses, the seller should become more desperate to sell and willing to drop prices.

**Our Approach:** 
Instead of making the AI "guess" what time it is, we use a rigid, math-driven time checker that tells the AI exactly how eager it needs to be. 
- **The Concept:** We calculate the exact minutes remaining until 4 PM. Based on that time limit, we assign a distinct "urgency zone" (e.g., Relaxed, Moderate, Urgent, Closing Soon).
- **The AI Guardrail:** Rather than just telling the AI "It's 3 PM, be desperate," we inject strict behavioral rules (e.g., *"Accept any offer above 70% of asking price"*) directly into the AI's core instructions on every single turn. This keeps the AI focused and prevents it from acting out of character over long conversations.

---

## 2. Multi-Item Handling & Haggling
**The Requirement:** 
The buyer should be able to browse inventory, haggle over prices, and buy multiple items (bundle deals) at once.

**Our Approach:**
We treated the AI like an employee who has access to a private company database. 
- **The Concept:** The AI cannot see the inventory or prices locally in its memory. When a user asks "what do you have?", the AI acts as a search engine, scanning the database tool. When a user wants to negotiate, the AI privately looks up the item's "asking price" and its "secret floor price" (the absolute minimum it can accept).
- **Bundling Logic:** If a buyer wants three items, the AI gathers the secret floor prices for all three, adds them up silently, and ensures the buyer's bulk offer combined clears that total bottom-line sum. This allows for fluid, human-like bundle negotiations without the store ever losing money.

---

## 3. Cash Transactions & Change
**The Requirement:** 
The system must handle monetary transactions, ensuring exact change is calculated and tracking the seller's initial cash box balance ($50).

**Our Approach:**
Large Language Models (LLMs) are notoriously bad at math. We solved this by strictly separating the *conversation* from the *calculator*.
- **The Concept:** The AI is strictly responsible for agreeing on a price and asking the buyer how much cash they are handing over. 
- **The Math Engine:** Once the buyer hands over the cash (e.g., a $100 bill for a $26 item), the AI hands the numbers off to a traditional, hardcoded Python calculator tool. The calculator verifies if there is enough money in the cash box to give $74 in change. If there is, it green-lights the sale. The AI simply relays the calculator's final answer back to the user in a friendly way.

---

## 4. App Orchestrated Natively by an LLM
**The Requirement:** 
The core application logic, tools, and flow should be orchestrated natively by the language model via tool-calling, rather than a pre-programmed state machine.

**Our Approach:**
We implemented the "ReAct" (Reason + Act) architecture.
- **The Concept:** Traditional chatbots are like train tracks (if user says X, do Y). Our system is an open sandbox. The user says something, the AI *reasons* about what tool it needs (e.g., "I need to check the cash box before making this sale"), *acts* by executing the tool, and then *observes* the result to formulate a human response. This means the conversation can go in completely unpredictable directions, and the AI handles it fluidly.

---

## 5. Simple State Persistence
**The Requirement:** 
Use a simple state file to keep track of inventory and money across different sessions, without heavy databases overhead.

**Our Approach:**
We used a single, lightweight JSON state file system that acts as the absolute source of truth.
- **The Concept:** Every time a sale is successfully completed, the system immediately updates a file on the computer (`sale_state.json`) with the new inventory status and the cash box total. When the user returns to the program hours or days later, it reads that file and picks up exactly where it left off. It is fully transparent, human-readable, and easily inspectable during a demo.
