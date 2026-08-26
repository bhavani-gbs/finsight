# FinSight Architecture

## 1. Architectural Objective

FinSight uses a hybrid architecture:

- **LLM layer:** understands natural language and extracts structured information.
- **Application layer:** validates input, manages conversation state, calculates financial facts, and applies decisions.
- **Database layer:** persists normalized financial records.

The LLM is not the financial source of truth.

---

## 2. High-Level Architecture

```text
                    +----------------+
                    |      User      |
                    +-------+--------+
                            |
                            v
                    +---------------+
                    |   Streamlit   |
                    |      UI       |
                    +-------+-------+
                            |
                            v
                +-----------------------+
                | ConversationController|
                +----------+------------+
                           |
             +-------------+-------------+
             |                           |
             v                           v
     +---------------+           +---------------+
     | Intent        |           | Transaction   |
     | Detection     |           | Parser       |
     +-------+-------+           +-------+-------+
             |                           |
             +-------------+-------------+
                           |
                           v
                  +----------------+
                  |    Validator   |
                  +-------+--------+
                          |
                          v
                  +---------------+
                  | Confirmation  |
                  +-------+-------+
                          |
                          v
                  +---------------+
                  | Transaction   |
                  | Service       |
                  +-------+-------+
                          |
                          v
                    +-----------+
                    |  SQLite   |
                    +-----+-----+
                          |
                          v
                +--------------------+
                | Financial State    |
                | Engine             |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Decision Engine    |
                +---------+----------+
                          |
                          v
                       Response
```

---

## 3. Separation of Responsibilities

### AI layer

The AI layer answers questions such as:

> "What transaction is the user describing?"

and:

> "What type of financial request is this?"

It should return structured information rather than directly modifying financial records.

### Core layer

The core layer owns:

- validation,
- database operations,
- financial calculations,
- business rules,
- decision generation.

### UI layer

The UI should only:

- display information,
- collect user input,
- maintain presentation state,
- invoke the controller.

---

## 4. Transaction Pipeline

```text
Raw user input
      |
      v
Intent Detection
      |
      +---- not a transaction ---> other handler
      |
      v
Transaction Parser
      |
      v
Structured Candidate
      |
      v
Candidate Validator
      |
      +---- invalid ---> clarification/error
      |
      v
Confirmation
      |
      +---- no ---> discard
      |
      +---- yes
             |
             v
      Transaction Service
             |
             v
          SQLite
             |
             v
      Financial State
             |
             v
       Decision Engine
```

---

## 5. Why Confirmation Exists

The parser is probabilistic.

Even when the model extracts:

```text
₹450
outgoing
food
Swiggy
```

the application does not immediately persist the transaction.

Instead:

```text
Model interpretation
        ↓
User verification
        ↓
Database persistence
```

This reduces the impact of:

- parsing mistakes,
- ambiguous natural language,
- incorrect merchant/category extraction,
- malformed model output.

---

## 6. Database Connection Strategy

The Streamlit application can rerun code in different execution contexts.

A persistent SQLite connection inside the session controller caused a thread error:

```text
SQLite objects created in a thread can only be used in that same thread.
```

The controller therefore stores only conversational state:

```python
self.account_id
self.state
self.pending_transaction
```

Database operations acquire a connection when needed:

```text
get_connection()
      ↓
database operation
      ↓
close connection
```

This avoids retaining a thread-bound SQLite connection in Streamlit session state.

---

## 7. Financial State

Financial state is recomputed from persistent records.

Conceptually:

```text
Confirmed transactions
        +
Active commitments
        +
Relevant goals
        ↓
Financial State
```

The current implementation exposes values such as:

- current balance,
- spendable balance.

The financial engine should remain deterministic.

---

## 8. Decision Engine

The decision engine receives a computed financial state and returns structured decisions.

Example:

```python
{
    "title": "...",
    "message": "...",
    "severity": "..."
}
```

The engine should not depend on Gemini for arithmetic.

Future rules can include:

- low spendable balance,
- upcoming large commitment,
- unusual spending,
- goal shortfall,
- risky discretionary purchase.

---

## 9. Intent Routing

Current routing concept:

```text
record_transaction
        → transaction pipeline

financial_query
        → financial state

spending_query
        → spending analysis

goal
        → goal management

commitment
        → commitment management

unknown
        → general assistant response
```

This architecture allows features to be added without rewriting the core conversation loop.

---

## 10. Future Input Adapters

All input methods should eventually converge into the same normalized transaction representation.

```text
Manual Input ───────┐
Forwarded SMS ──────┤
Screenshot ─────────┼──> Transaction Candidate
Future API ─────────┘
                           |
                           v
                       Validation
                           |
                           v
                      Confirmation
                           |
                           v
                         SQLite
```

This avoids creating separate financial logic for each input source.

---

## 11. Security Boundary

The intended security boundary is:

```text
Raw external content
       ↓
Parsing
       ↓
Minimal normalized data
       ↓
Application validation
       ↓
Database
```

The parser should not automatically persist arbitrary raw messages.

---

## 12. Future Scalability

For a production version:

- SQLite can be replaced with PostgreSQL.
- Authentication can be introduced.
- A proper API layer can separate frontend/backend.
- Database connection pooling can replace per-operation SQLite connections.
- Background jobs can handle heavier processing.
- Model providers can be abstracted behind an AI interface.

These are not required for the current academic prototype.
