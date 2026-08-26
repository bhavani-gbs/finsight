# FinSight

FinSight is a conversational personal-finance assistant designed primarily for students. It helps users record transactions, understand their current financial position, and eventually make safer spending decisions by combining natural-language interaction with deterministic financial logic.

## Current MVP

The current prototype provides an end-to-end conversational transaction flow:

1. User enters a transaction in natural language.
2. Gemini extracts structured transaction information.
3. A validation layer checks the extracted candidate.
4. FinSight asks the user for confirmation.
5. The confirmed transaction is persisted in SQLite.
6. The financial state is recalculated.
7. The decision engine evaluates the updated state.
8. The assistant returns the resulting financial information.

The prototype also supports financial queries for current balance, spendable balance, and financial summary.

### Demonstrated inputs

- Manually typed transactions
- Forwarded/copied bank or UPI transaction SMS
- Incoming transactions
- Outgoing transactions

### Explicitly out of scope for the current MVP

- Direct bank APIs
- Automatic phone SMS/notification reading
- WhatsApp integration
- Automatic account synchronization
- PDF bank-statement workflows
- CSV bank-statement workflows

These may be considered future extensions rather than MVP requirements.

---

## Project Goal

The goal of FinSight is not merely to record expenses. It is to help students understand:

- how much money they currently have,
- how much is realistically available to spend,
- what financial obligations are approaching,
- whether spending may interfere with goals,
- and what action would be financially sensible.

The central design principle is:

> **LLMs interpret user input; deterministic application logic calculates financial facts and makes rule-based decisions.**

This prevents the language model from becoming the source of truth for balances or financial calculations.

---

## Core Architecture

```text
User
 |
 v
Streamlit Chat UI
 |
 v
Conversation Controller
 |
 +--------------------+
 |                    |
 v                    v
Intent Detection    Transaction Parser
 |                    |
 +---------+----------+
           |
           v
       Validation
           |
           v
      Confirmation
           |
           v
       SQLite DB
           |
           v
   Financial State Engine
           |
           v
    Decision Engine
           |
           v
     User Response
```

---

## Main Components

### `app.py`

Streamlit presentation layer.

Responsibilities:

- initialize the database,
- load the demo user/account,
- maintain conversational UI state,
- display chat history,
- pass user messages to the conversation controller.

### `core/conversation.py`

Conversation orchestration layer.

Responsibilities:

- maintain conversation state,
- route messages according to detected intent,
- manage transaction confirmation,
- invoke transaction services,
- retrieve financial state,
- format responses.

### `ai/parser.py`

Gemini-powered transaction parser.

Converts natural-language input into a structured transaction candidate such as:

```json
{
  "is_transaction": true,
  "amount": 450,
  "transaction_type": "outgoing",
  "category": "food",
  "merchant": "Swiggy",
  "description": null
}
```

### `ai/assistant.py`

Validation layer for model-generated transaction candidates.

It prevents incomplete or invalid candidates from being persisted.

### `ai/intent.py`

Classifies user messages into high-level intents such as:

- `record_transaction`
- `financial_query`
- `spending_query`
- `goal`
- `commitment`
- `unknown`

Financial query types currently include:

- `current_balance`
- `spendable_balance`
- `financial_summary`
- `upcoming_commitments`
- `savings`

### `core/transaction.py`

Transaction service layer.

Responsibilities:

- validate transaction fields,
- insert transactions,
- retrieve transactions,
- confirm/discard transactions.

### `core/financial_state.py`

Calculates financial state from persisted records.

The financial state is derived rather than treated as an independently stored number.

### `core/decision_engine.py`

Evaluates the financial state using deterministic rules and returns actionable decisions/attention items.

### `database/`

Contains:

- SQLite connection handling,
- schema initialization,
- demo-data seeding.

---

## Database Model

The current schema contains:

### `users`

Stores user-level profile information.

### `accounts`

Represents financial accounts belonging to a user.

### `transactions`

Stores normalized financial events.

Important fields include:

- account
- amount
- transaction type
- category
- merchant
- description
- transaction date
- status
- source

### `commitments`

Stores recurring or upcoming financial obligations.

### `goals`

Stores savings targets.

### `financial_intents`

Stores planned or considered financial actions.

---

## Financial State

FinSight distinguishes between:

### Current balance

The user's current financial balance derived from confirmed transactions.

### Spendable balance

The amount that is realistically available after accounting for relevant financial obligations represented by the application.

For example:

```text
Current balance      ₹13,735
Commitments            ₹5,000
-----------------------------
Spendable balance     ₹8,735
```

The exact calculation is performed by application code, not by Gemini.

---

## Privacy Approach

The Phase-1 input model deliberately avoids automatic access to private phone data.

Users explicitly provide transaction information by:

- typing it,
- forwarding/copying a bank or UPI SMS,
- or, in a future Phase-1 extension, providing a screenshot.

FinSight should normalize the transaction and retain only the information required for financial functionality.

Sensitive details such as full account numbers, full UPI IDs, phone numbers, and unrelated SMS content should not be unnecessarily persisted.

---

## Running the Project

### 1. Create and activate the virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Configure Gemini

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_selected_gemini_model
```

Do not commit `.env`.

### 4. Initialize/seed demo data

```bash
python3 -m database.seed
```

Only run the seed command when you intentionally want to create/reset the demo data according to the seed implementation.

### 5. Run tests

Examples:

```bash
python3 -m tests.test_parser
python3 -m tests.test_conversation
```

### 6. Run the Streamlit prototype

```bash
python3 -m streamlit run app.py
```

---

## Demo Flow

A recommended demonstration is:

```text
User:
I spent 385 on Zomato

FinSight:
I detected this transaction:
₹385.00 — outgoing — food — Zomato
Would you like me to record it?

User:
yes

FinSight:
Transaction recorded.
Current balance: ...
Spendable balance: ...
```

Then demonstrate:

```text
What's my current balance?
```

and:

```text
How much can I spend?
```

An incoming bank/UPI SMS can also be pasted to demonstrate that incoming transactions increase the financial state.

---

## Current Limitations

The following are intentionally unfinished:

- spending aggregation/analysis,
- full commitment queries,
- goal creation and tracking through conversation,
- goal-aware spending recommendations,
- screenshot transaction extraction,
- richer conversational financial context,
- duplicate SMS/reference detection,
- comprehensive error handling,
- production authentication,
- deployment hardening.

These belong to subsequent development phases.

---

## Roadmap

### Phase 1 — Core MVP
- Natural-language transactions
- Confirmation
- Persistent financial records
- Financial state
- Basic financial queries
- Rule-based decisions
- Streamlit prototype

### Phase 2 — Financial Intelligence
- Spending analysis
- Commitment management
- Goal management
- Goal/commitment-aware recommendations
- Better financial summaries

### Phase 3 — Input Expansion & Robustness
- Screenshot parsing
- Duplicate transaction detection
- Better date/reference extraction
- Improved error handling
- Privacy hardening

### Phase 4 — Advanced Intelligence
- Forecasting
- Personalized financial patterns
- Optional ML models
- More advanced recommendation logic

Direct bank integration and automatic notification reading remain separate future considerations.

---

## Technology Stack

- Python
- SQLite
- Streamlit
- Google Gemini API
- `google-genai`
- `python-dotenv`

The system intentionally combines probabilistic language understanding with deterministic financial computation.
