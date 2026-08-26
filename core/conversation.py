from ai.parser import parse_transaction
from ai.assistant import validate_transaction_candidate
from core.transaction import (
    create_transaction,
    confirm_transaction,
)
from core.financial_state import calculate_financial_state
from core.decision_engine import evaluate_financial_state


class ConversationController:

    def __init__(self, connection, account_id):

        self.connection = connection
        self.account_id = account_id

        self.state = "IDLE"
        self.pending_transaction = None

    def handle_message(self, message):

        message = message.strip()

        if not message:
            return "Please enter a message."

        # --------------------------------------------------
        # CONFIRMATION STATE
        # --------------------------------------------------

        if self.state == "AWAITING_CONFIRMATION":

            return self._handle_confirmation(message)

        # --------------------------------------------------
        # NORMAL STATE
        # --------------------------------------------------

        parsed = parse_transaction(message)

        validated = validate_transaction_candidate(parsed)

        if not validated["is_transaction"]:

            return (
                "I didn't detect a transaction. "
                "You can tell me about an income, expense, "
                "goal, or commitment."
            )

        self.pending_transaction = validated

        self.state = "AWAITING_CONFIRMATION"

        return self._confirmation_message(validated)

    def _confirmation_message(self, transaction):

        amount = transaction["amount"]
        transaction_type = transaction["transaction_type"]
        category = transaction["category"]
        merchant = transaction["merchant"]

        details = f"₹{amount:,.2f} — {transaction_type}"

        if category:
            details += f" — {category}"

        if merchant:
            details += f" — {merchant}"

        return (
            "I detected this transaction:\n\n"
            f"**{details}**\n\n"
            "Would you like me to record it?"
        )

    def _handle_confirmation(self, message):

        normalized = message.lower()

        if normalized in {
            "yes",
            "y",
            "confirm",
            "confirmed",
            "record it",
        }:

            transaction = self.pending_transaction

            transaction_id = create_transaction(
                connection=self.connection,
                account_id=self.account_id,
                amount=transaction["amount"],
                transaction_type=transaction["transaction_type"],
                category=transaction["category"],
                merchant=transaction["merchant"],
                description=transaction["description"],
                source="manual",
                status="confirmed",
            )

            self.pending_transaction = None
            self.state = "IDLE"

            financial_state = calculate_financial_state(
                self.connection
            )

            decisions = evaluate_financial_state(
                financial_state
            )

            response = (
                f"✅ Transaction recorded.\n\n"
                f"Current balance: "
                f"₹{financial_state.current_balance:,.2f}\n"
                f"Spendable balance: "
                f"₹{financial_state.spendable_balance:,.2f}"
            )

            if decisions:

                response += "\n\n⚠️ Attention:\n"

                for decision in decisions:
                    response += (
                        f"- {decision['title']}\n"
                    )

            return response

        if normalized in {
            "no",
            "n",
            "cancel",
            "discard",
        }:

            self.pending_transaction = None
            self.state = "IDLE"

            return "Transaction discarded."

        return (
            "Please confirm the transaction with "
            "**yes** or **no**."
        )