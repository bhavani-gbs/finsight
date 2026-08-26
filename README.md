# FinSight

> An AI-powered personal financial companion designed to help students
> understand their finances and make better financial decisions.

## Overview

FinSight is a privacy-conscious financial assistant that helps users
track transactions, manage commitments and savings goals, reconcile
financial discrepancies, and receive actionable financial insights.

Unlike a traditional expense tracker, FinSight focuses on helping users
make better financial decisions rather than simply recording transactions.

## Core Principles

- User control over financial data
- Persist user-authored financial facts
- Compute derived financial state
- AI assists reasoning but does not own financial logic
- Transactions require user confirmation
- Minimal and relevant AI context
- Proactive notifications only for critical events
- Graceful degradation when AI services are unavailable

## MVP

The current prototype supports:

- Natural-language transaction entry
- Transaction confirmation
- Financial state calculation
- Savings goals
- Financial commitments
- Reconciliation
- Critical financial alerts
- AI-powered conversational assistance

## Planned

- Forwarded bank/UPI notification parsing
- Screenshot transaction extraction
- WhatsApp integration
- Automatic transaction reading
- Bank integrations

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Product Decisions

See [`docs/PRODUCT_DECISIONS.md`](docs/PRODUCT_DECISIONS.md).

## Demo

See [`docs/DEMO.md`](docs/DEMO.md).

## Technology

- Python
- Streamlit
- SQLite
- Google Gemini API