import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite",
)


INTENT_PROMPT = """
You are the intent classifier for a personal financial assistant.

Classify the user's message into exactly ONE of these intents:

record_transaction
financial_query
spending_query
goal
commitment
unknown

For financial_query, also determine query_type.

Allowed query_type values:
- current_balance
- spendable_balance
- financial_summary
- upcoming_commitments
- savings
- none

Return ONLY valid JSON.

Examples:

User:
"I spent 450 on food at Swiggy"

Output:
{
  "intent": "record_transaction",
  "query_type": "none"
}

User:
"What's my current balance?"

Output:
{
  "intent": "financial_query",
  "query_type": "current_balance"
}

User:
"How much can I spend?"

Output:
{
  "intent": "financial_query",
  "query_type": "spendable_balance"
}

User:
"How much have I spent on food?"

Output:
{
  "intent": "spending_query",
  "query_type": "none"
}

User:
"I want to save 10000 for headphones"

Output:
{
  "intent": "goal",
  "query_type": "none"
}

User:
"I have to pay 5000 for hostel next month"

Output:
{
  "intent": "commitment",
  "query_type": "none"
}
"""


VALID_INTENTS = {
    "record_transaction",
    "financial_query",
    "spending_query",
    "goal",
    "commitment",
    "unknown",
}


VALID_QUERY_TYPES = {
    "current_balance",
    "spendable_balance",
    "financial_summary",
    "upcoming_commitments",
    "savings",
    "none",
}


def detect_intent(message):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            INTENT_PROMPT,
            f"\nUser message:\n{message}",
        ],
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "", 1)
        text = text.replace("```", "", 1)
        text = text.strip()

    try:
        result = json.loads(text)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini returned invalid intent JSON."
        ) from error

    validate_intent(result)

    return result


def validate_intent(data):

    if not isinstance(data, dict):
        raise ValueError(
            "Intent classifier must return an object."
        )

    if "intent" not in data:
        raise ValueError(
            "Intent is missing."
        )

    if "query_type" not in data:
        raise ValueError(
            "Query type is missing."
        )

    if data["intent"] not in VALID_INTENTS:
        raise ValueError(
            f"Invalid intent: {data['intent']}"
        )

    if data["query_type"] not in VALID_QUERY_TYPES:
        raise ValueError(
            f"Invalid query type: {data['query_type']}"
        )

    if (
        data["intent"] == "financial_query"
        and data["query_type"] == "none"
    ):
        raise ValueError(
            "Financial query requires a query type."
        )

    return data