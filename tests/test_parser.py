from ai.parser import parse_transaction
from ai.assistant import validate_transaction_candidate


messages = [
    "I spent 450 on food at Swiggy",
    "My dad sent me 5000",
    "I bought something",
    "I spent 450",
    "How much did I spend this month?",
]


for message in messages:

    print("\nUSER:", message)

    try:
        result = parse_transaction(message)

        print("RAW:", result)

        validated = validate_transaction_candidate(result)

        print("VALID:", validated)

    except Exception as error:
        print("ERROR:", error)