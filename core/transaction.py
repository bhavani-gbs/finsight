from datetime import datetime


VALID_TYPES = {"incoming", "outgoing", "transfer"}
VALID_STATUSES = {"pending", "confirmed", "failed", "refunded","discarded"}
VALID_SOURCES = {"manual", "sms", "screenshot","seed"}


def validate_transaction(
    amount,
    transaction_type,
    transaction_date,
    source,
    status="pending",
):
    if amount <= 0:
        raise ValueError("Transaction amount must be greater than zero.")

    if transaction_type not in VALID_TYPES:
        raise ValueError(f"Invalid transaction type: {transaction_type}")

    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid transaction status: {status}")

    if source not in VALID_SOURCES:
        raise ValueError(f"Invalid transaction source: {source}")

    if not transaction_date:
        raise ValueError("Transaction date is required.")


def create_transaction(
    connection,
    account_id,
    amount,
    transaction_type,
    category=None,
    merchant=None,
    description=None,
    transaction_date=None,
    source="manual",
    status="pending",
):
    transaction_date = transaction_date or datetime.now().isoformat()

    validate_transaction(
        amount=amount,
        transaction_type=transaction_type,
        transaction_date=transaction_date,
        source=source,
        status=status,
    )

    cursor = connection.execute(
        """
        INSERT INTO transactions (
            account_id,
            amount,
            transaction_type,
            category,
            merchant,
            description,
            transaction_date,
            status,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            account_id,
            amount,
            transaction_type,
            category,
            merchant,
            description,
            transaction_date,
            status,
            source,
        ),
    )

    connection.commit()

    return cursor.lastrowid

def get_transactions(connection, account_id=None, status=None):
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if account_id is not None:
        query += " AND account_id = ?"
        params.append(account_id)

    if status is not None:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY transaction_date DESC"

    return connection.execute(query, params).fetchall()

def confirm_transaction(connection, transaction_id):
    connection.execute(
        """
        UPDATE transactions
        SET status = 'confirmed'
        WHERE id = ?
        """,
        (transaction_id,),
    )

    connection.commit()
    
def discard_transaction(connection, transaction_id):
    connection.execute(
        """
        UPDATE transactions
        SET status = 'discarded'
        WHERE id = ?
        """,
        (transaction_id,),
    )

    connection.commit()