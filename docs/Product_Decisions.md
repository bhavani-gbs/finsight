# FinSight Design Decisions

This document records the major product and architecture decisions made for FinSight.

## 1. Primary Target User

**Decision:** Students are the primary target.

**Reason:** Students often need simple financial awareness and guidance without the complexity of full personal-finance software.

The product goal is to improve financial independence and decision-making.

---

## 2. Conversational Interface

**Decision:** Use a chatbot-style conversational interface as the primary interaction model.

**Reason:** Students can describe transactions and financial situations naturally instead of navigating multiple forms.

Streamlit is currently used for the prototype UI.

---

## 3. Transaction Confirmation

**Decision:** Every AI-parsed transaction requires user confirmation before persistence.

**Reason:** LLM extraction is probabilistic. Confirmation creates a safety boundary before modifying financial records.

Flow:

```text
Input → Parse → Validate → Confirm → Persist
```

---

## 4. LLM vs Deterministic Logic

**Decision:** Gemini handles interpretation, while Python application logic handles financial facts.

**LLM responsibilities:**

- intent classification,
- transaction extraction,
- natural-language understanding.

**Deterministic responsibilities:**

- validation,
- database operations,
- balance calculation,
- spendable-balance calculation,
- decision rules.

**Reason:** Financial numbers should be reproducible and auditable.

---

## 5. Transaction Sources

Current supported sources:

- `manual`
- `sms`
- `screenshot` (schema-supported/future input path)
- `seed` for demo data

The current UI can accept manually typed text and copied/forwarded bank/UPI SMS content.

---

## 6. No Automatic SMS Reading in Phase 1

**Decision:** FinSight does not automatically read phone notifications or SMS.

**Reason:**

- privacy concerns,
- platform permissions,
- unnecessary complexity for the prototype,
- user-controlled input is sufficient to demonstrate the concept.

The user explicitly supplies the SMS content.

---

## 7. No Direct Bank APIs in Phase 1

**Decision:** Do not integrate bank APIs yet.

**Reason:**

- API availability and authentication complexity,
- security burden,
- unnecessary for proving the core product concept.

Bank APIs can be considered later.

---

## 8. No PDF/CSV Workflow in the Initial Prototype

**Decision:** PDF and CSV statement uploads are not prioritized.

**Reason:** Students are less likely to manually go through the extra process of exporting and uploading statements compared with simply forwarding/copying a transaction message.

---

## 9. Privacy by Minimization

**Decision:** Do not retain unnecessary sensitive information from transaction messages.

Avoid storing:

- full account numbers,
- full UPI IDs,
- phone numbers,
- unrelated SMS content.

Only normalized financial information required by FinSight should be retained.

---

## 10. Financial State vs Persistent Records

**Decision:** Persist the financial records; recompute derived financial state.

Persistent:

- transaction records,
- user profile,
- accounts,
- goals,
- commitments.

Recomputable:

- current balance,
- spendable balance,
- aggregated spending,
- derived recommendations.

**Reason:** Derived values can become stale. Recomputing them from source records provides consistency.

---

## 11. Conversation State

**Decision:** Keep only short-lived conversational state in the controller.

Current state includes:

- `IDLE`
- `AWAITING_CONFIRMATION`
- pending transaction candidate.

The SQLite connection is deliberately not stored in the controller.

---

## 12. SQLite Connection Handling

**Decision:** Open database connections when required and close them after the operation.

**Reason:** Streamlit execution can involve different threads/reruns. Keeping a SQLite connection in persistent session state caused thread-affinity errors.

---

## 13. Spendable Balance

**Decision:** Distinguish current balance from spendable balance.

Current balance answers:

> How much money exists?

Spendable balance answers:

> How much money can reasonably be used after accounting for relevant obligations?

This distinction is central to FinSight's financial guidance.

---

## 14. Rule-Based Decision Engine

**Decision:** Start with deterministic rules rather than an LLM-only recommendation system.

**Reason:**

- predictable behavior,
- easier testing,
- explainability,
- easier demonstration to faculty,
- no hallucinated financial arithmetic.

ML/forecasting can be introduced later where historical data makes it useful.

---

## 15. Goals and Commitments

**Decision:** Treat goals and commitments as first-class financial entities.

A transaction history alone is insufficient for decision support.

Commitments represent obligations.

Goals represent intended future savings or financial targets.

Together they allow FinSight to reason about future financial impact.

---

## 16. Input Adapter Architecture

**Decision:** Different input methods should converge into the same normalized transaction pipeline.

```text
Manual
SMS
Screenshot
Future API
   ↓
Normalized Candidate
   ↓
Validation
   ↓
Confirmation
   ↓
Transaction Service
```

This avoids duplicating financial logic.

---

## 17. Phase-1 Product Boundary

The prototype is intentionally not a complete banking application.

Phase 1 focuses on:

- transaction capture,
- financial state,
- basic queries,
- decision foundation,
- conversational interaction.

Advanced integrations are future scope.
