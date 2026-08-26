from database.db import get_connection, initialize_database
from core.transaction import (
    create_transaction,
    get_transactions,
    confirm_transaction,
)
from core.financial_state import calculate_financial_state
from core.decision_engine import evaluate_financial_state

initialize_database()

connection = get_connection()

'''# Create a test user
cursor = connection.execute(
    "INSERT INTO users (name) VALUES (?)",
    ("Demo User",),
)
user_id = cursor.lastrowid

# Create account
cursor = connection.execute(
    """
    INSERT INTO accounts (user_id, name, account_type)
    VALUES (?, ?, ?)
    """,
    (user_id, "SBI", "bank"),
)
account_id = cursor.lastrowid

connection.commit()

# Create transaction
transaction_id = create_transaction(
    connection=connection,
    account_id=account_id,
    amount=450,
    transaction_type="outgoing",
    category="food",
    merchant="Swiggy",
    description="Lunch",
    source="manual",
)

print("Created transaction:", transaction_id)

transactions = get_transactions(connection)

for transaction in transactions:
    print(dict(transaction))

confirm_transaction(connection, transaction_id)

print("Transaction confirmed.")'''

state = calculate_financial_state(connection)

print("\nFINANCIAL STATE")
print("----------------")
print("Incoming:", state.total_incoming)
print("Outgoing:", state.total_outgoing)
print("Balance:", state.current_balance)
print("Commitments:", state.upcoming_commitments)
print("Spendable:", state.spendable_balance)
print("Accounts:", state.account_balances)

decisions = evaluate_financial_state(state)

print("\nDECISIONS")
print("----------------")

for decision in decisions:
    print(decision)

connection.close()