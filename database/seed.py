from database.db import get_connection, initialize_database
from core.transaction import create_transaction, confirm_transaction


def seed_demo_data():
    initialize_database()

    connection = get_connection()

    # --------------------------------------------------
    # CLEAR EXISTING DATA
    # --------------------------------------------------

    connection.execute("DELETE FROM transactions")
    connection.execute("DELETE FROM commitments")
    connection.execute("DELETE FROM goals")
    connection.execute("DELETE FROM financial_intents")
    connection.execute("DELETE FROM accounts")
    connection.execute("DELETE FROM users")

    connection.commit()

    # --------------------------------------------------
    # CREATE DEMO USER
    # --------------------------------------------------

    cursor = connection.execute(
        """
        INSERT INTO users (name, currency)
        VALUES (?, ?)
        """,
        ("Demo Student", "INR"),
    )

    user_id = cursor.lastrowid

    # --------------------------------------------------
    # CREATE ACCOUNT
    # --------------------------------------------------

    cursor = connection.execute(
        """
        INSERT INTO accounts (
            user_id,
            name,
            account_type
        )
        VALUES (?, ?, ?)
        """,
        (user_id, "Main Account", "bank"),
    )

    account_id = cursor.lastrowid

    connection.commit()

    # --------------------------------------------------
    # INCOME
    # --------------------------------------------------

    income_id = create_transaction(
        connection=connection,
        account_id=account_id,
        amount=25000,
        transaction_type="incoming",
        category="income",
        merchant="Monthly Allowance",
        description="Monthly student allowance",
        source="seed",
    )

    confirm_transaction(
        connection,
        income_id,
    )

    # --------------------------------------------------
    # EXISTING EXPENSES
    # --------------------------------------------------

    expenses = [
        ("food", "Food & Dining", 4000),
        ("transport", "Transport", 2000),
        ("shopping", "Shopping", 3500),
        ("entertainment", "Entertainment", 1500),
        ("other", "Other", 1000),
    ]

    for category, merchant, amount in expenses:

        transaction_id = create_transaction(
            connection=connection,
            account_id=account_id,
            amount=amount,
            transaction_type="outgoing",
            category=category,
            merchant=merchant,
            description=None,
            source="seed",
        )

        confirm_transaction(
            connection,
            transaction_id,
        )

    # --------------------------------------------------
    # UPCOMING COMMITMENT
    # --------------------------------------------------

    connection.execute(
        """
        INSERT INTO commitments (
            user_id,
            name,
            amount,
            due_date,
            frequency,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            "Hostel Fee",
            5000,
            "2026-09-01",
            "monthly",
            "active",
        ),
    )

    # --------------------------------------------------
    # SAVINGS GOAL
    # --------------------------------------------------

    connection.execute(
        """
        INSERT INTO goals (
            user_id,
            name,
            target_amount,
            current_amount,
            deadline,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            "New Headphones",
            10000,
            3000,
            "2026-11-30",
            "active",
        ),
    )

    connection.commit()
    connection.close()

    print("Demo data seeded successfully.")


if __name__ == "__main__":
    seed_demo_data()