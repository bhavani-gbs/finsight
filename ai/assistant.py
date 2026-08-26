REQUIRED_TRANSACTION_FIELDS = {
    "is_transaction",
    "amount",
    "transaction_type",
    "category",
    "merchant",
    "description",
}


def validate_transaction_candidate(data):

    if not isinstance(data, dict):
        raise ValueError("Transaction parser must return an object.")

    missing = REQUIRED_TRANSACTION_FIELDS - set(data.keys())

    if missing:
        raise ValueError(
            f"Missing transaction fields: {missing}"
        )

    if not data["is_transaction"]:
        return data

    if data["amount"] is None:
        raise ValueError("Transaction amount is missing.")

    if data["amount"] <= 0:
        raise ValueError("Transaction amount must be positive.")

    if data["transaction_type"] is None:
        raise ValueError("Transaction type is missing.")

    if data["transaction_type"] not in {
        "incoming",
        "outgoing",
        "transfer",
    }:
        raise ValueError("Invalid transaction type.")

    return data