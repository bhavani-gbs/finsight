from ai.intent import detect_intent


messages = [
    "I spent 450 on food at Swiggy",
    "My dad sent me 5000",
    "What's my current balance?",
    "How much can I spend?",
    "How much have I spent on food?",
    "I want to save 10000 for headphones",
    "I have to pay 5000 for hostel next month",
    "Tell me something interesting",
]


for message in messages:

    print("\nUSER:", message)

    try:
        result = detect_intent(message)

        print("INTENT:", result)

    except Exception as error:

        print("ERROR:", error)