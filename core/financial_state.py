from dataclasses import dataclass, field


@dataclass
class FinancialState:
    total_incoming: float = 0.0
    total_outgoing: float = 0.0
    current_balance: float = 0.0
    upcoming_commitments: float = 0.0
    spendable_balance: float = 0.0
    account_balances: dict = field(default_factory=dict)
    goal_progress: list = field(default_factory=list)

def calculate_transaction_totals(connection):
    rows = connection.execute(
        """
        SELECT transaction_type, SUM(amount) AS total
        FROM transactions
        WHERE status = 'confirmed'
        GROUP BY transaction_type
        """
    ).fetchall()

    incoming = 0.0
    outgoing = 0.0

    for row in rows:
        if row["transaction_type"] == "incoming":
            incoming = row["total"] or 0.0

        elif row["transaction_type"] == "outgoing":
            outgoing = row["total"] or 0.0

    return incoming, outgoing

def calculate_account_balances(connection):
    rows = connection.execute(
        """
        SELECT
            accounts.id,
            accounts.name,
            accounts.account_type,
            COALESCE(
                SUM(
                    CASE
                        WHEN transactions.transaction_type = 'incoming'
                            THEN transactions.amount
                        WHEN transactions.transaction_type = 'outgoing'
                            THEN -transactions.amount
                        ELSE 0
                    END
                ),
                0
            ) AS balance

        FROM accounts

        LEFT JOIN transactions
            ON accounts.id = transactions.account_id
            AND transactions.status = 'confirmed'

        GROUP BY accounts.id
        """
    ).fetchall()

    balances = {}

    for row in rows:
        balances[row["name"]] = {
            "balance": row["balance"],
            "type": row["account_type"],
        }

    return balances

def calculate_commitments(connection):
    row = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM commitments
        WHERE status = 'active'
        """
    ).fetchone()

    return row["total"] or 0.0

def calculate_financial_state(connection):
    incoming, outgoing = calculate_transaction_totals(connection)

    current_balance = incoming - outgoing

    commitments = calculate_commitments(connection)

    spendable_balance = (
        current_balance
        - commitments
    )

    account_balances = calculate_account_balances(connection)

    goals = connection.execute(
        """
        SELECT
            id,
            name,
            target_amount,
            current_amount,
            deadline,
            status
        FROM goals
        WHERE status = 'active'
        """
    ).fetchall()

    goal_progress = []

    for goal in goals:
        progress = (
            goal["current_amount"] / goal["target_amount"]
            if goal["target_amount"] > 0
            else 0
        )

        goal_progress.append({
            "id": goal["id"],
            "name": goal["name"],
            "target": goal["target_amount"],
            "current": goal["current_amount"],
            "progress": progress,
            "deadline": goal["deadline"],
        })

    return FinancialState(
        total_incoming=incoming,
        total_outgoing=outgoing,
        current_balance=current_balance,
        upcoming_commitments=commitments,
        spendable_balance=spendable_balance,
        account_balances=account_balances,
        goal_progress=goal_progress,
    )