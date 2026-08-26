from database.db import get_connection, initialize_database
from core.conversation import ConversationController


initialize_database()

connection = get_connection()


# Create user
cursor = connection.execute(
    "INSERT INTO users (name) VALUES (?)",
    ("Demo User",),
)

user_id = cursor.lastrowid


# Create account
cursor = connection.execute(
    """
    INSERT INTO accounts (
        user_id,
        name,
        account_type
    )
    VALUES (?, ?, ?)
    """,
    (user_id, "SBI", "bank"),
)

account_id = cursor.lastrowid

connection.commit()


controller = ConversationController(
    connection=connection,
    account_id=account_id,
)


print("\nUSER:")
print("I spent 450 on food at Swiggy")

response = controller.handle_message(
    "I spent 450 on food at Swiggy"
)

print("\nFINSIGHT:")
print(response)


print("\nUSER:")
print("yes")

response = controller.handle_message("yes")

print("\nFINSIGHT:")
print(response)


connection.close()