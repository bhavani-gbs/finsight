def check_commitment_risk(financial_state):
    if (
        financial_state.upcoming_commitments > 0
        and financial_state.spendable_balance
        < financial_state.upcoming_commitments
    ):
        return {
            "type": "commitment_risk",
            "severity": "critical",
            "title": "Upcoming commitment risk",
            "data": {
                "spendable_balance": financial_state.spendable_balance,
                "commitments": financial_state.upcoming_commitments,
            },
        }

    return None

def check_low_buffer(financial_state, threshold=3000):
    if (
        financial_state.spendable_balance >= 0
        and financial_state.spendable_balance < threshold
    ):
        return {
            "type": "low_buffer",
            "severity": "warning",
            "title": "Low financial buffer",
            "data": {
                "spendable_balance": financial_state.spendable_balance,
                "threshold": threshold,
            },
        }

    return None

def check_goal_progress(financial_state):
    decisions = []

    for goal in financial_state.goal_progress:
        if goal["target"] <= 0:
            continue

        progress = goal["progress"]

        if progress < 0.25:
            decisions.append({
                "type": "goal_progress",
                "severity": "info",
                "title": "Goal needs attention",
                "data": {
                    "goal": goal["name"],
                    "progress": progress,
                    "current": goal["current"],
                    "target": goal["target"],
                },
            })

    return decisions

def evaluate_financial_state(financial_state):
    decisions = []

    commitment_risk = check_commitment_risk(financial_state)

    if commitment_risk:
        decisions.append(commitment_risk)

    low_buffer = check_low_buffer(financial_state)

    if low_buffer:
        decisions.append(low_buffer)

    decisions.extend(
        check_goal_progress(financial_state)
    )

    return decisions