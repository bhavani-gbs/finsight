import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


MODEL_NAME = "gemini-3.5-flash-lite"


TRANSACTION_PROMPT = """
You are a financial transaction parser.

Extract transaction information from the user's message.

Return ONLY valid JSON.

Required fields:
- is_transaction: boolean
- amount: number or null
- transaction_type: "incoming", "outgoing", "transfer", or null
- category: string or null
- merchant: string or null
- description: string or null

Rules:
- Never invent missing information.
- If the amount is unclear, return null.
- If incoming/outgoing cannot be determined, return null.
- Category can be null.
- Merchant can be null.
- Do not calculate anything.
- Do not provide explanations.

Examples:

User:
"I spent 450 on food at Swiggy"

Output:
{
  "is_transaction": true,
  "amount": 450,
  "transaction_type": "outgoing",
  "category": "food",
  "merchant": "Swiggy",
  "description": null
}

User:
"My dad sent me 5000"

Output:
{
  "is_transaction": true,
  "amount": 5000,
  "transaction_type": "incoming",
  "category": "income",
  "merchant": null,
  "description": null
}

User:
"Hey, how much did I spend this month?"

Output:
{
  "is_transaction": false,
  "amount": null,
  "transaction_type": null,
  "category": null,
  "merchant": null,
  "description": null
}
"""


def parse_transaction(message):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            TRANSACTION_PROMPT,
            f"\nUser message:\n{message}"
        ],
    )

    text = response.text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Gemini returned invalid JSON.")