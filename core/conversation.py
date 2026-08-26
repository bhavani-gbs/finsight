from ai.parser import parse_transaction
from database.db import get_connection
from ai.assistant import validate_transaction_candidate
from ai.intent import detect_intent

from core.transaction import create_transaction
from core.financial_state import calculate_financial_state
from core.decision_engine import evaluate_financial_state


class ConversationController:

    def __init__(self, account_id):

        self.account_id = account_id
        self.state = "IDLE"
        self.pending_transaction = None

    # ==================================================
    # MAIN MESSAGE HANDLER
    # ==================================================

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
        # INTENT DETECTION
        # --------------------------------------------------

        intent = detect_intent(message)

        # --------------------------------------------------
        # TRANSACTION
        # --------------------------------------------------

        if intent["intent"] == "record_transaction":

            return self._handle_transaction(message)

        # --------------------------------------------------
        # FINANCIAL QUERY
        # --------------------------------------------------

        if intent["intent"] == "financial_query":

            return self._handle_financial_query(
                intent["query_type"]
            )

        # --------------------------------------------------
        # SPENDING QUERY
        # --------------------------------------------------

        if intent["intent"] == "spending_query":

            return self._handle_spending_query(message)

        # --------------------------------------------------
        # GOAL / COMMITMENT / UNKNOWN
        # --------------------------------------------------

        return (
            "I can help you track transactions, "
            "understand your spending, manage goals, "
            "and keep track of commitments."
        )

    # ==================================================
    # TRANSACTION HANDLING
    # ==================================================

    def _handle_transaction(self, message):

        parsed = parse_transaction(message)

        validated = validate_transaction_candidate(
            parsed
        )

        if not validated["is_transaction"]:

            return (
                "I didn't detect a transaction. "
                "Could you tell me what you spent "
                "or received?"
            )

        self.pending_transaction = validated
        self.state = "AWAITING_CONFIRMATION"

        return self._confirmation_message(
            validated
        )

    # ==================================================
    # CONFIRMATION MESSAGE
    # ==================================================

    def _confirmation_message(self, transaction):

        amount = transaction["amount"]
        transaction_type = transaction["transaction_type"]
        category = transaction["category"]
        merchant = transaction["merchant"]

        details = (
            f"₹{amount:,.2f} — "
            f"{transaction_type}"
        )

        if category:
            details += f" — {category}"

        if merchant:
            details += f" — {merchant}"

        return (
            "I detected this transaction:\n\n"
            f"**{details}**\n\n"
            "Would you like me to record it?"
        )

    # ==================================================
    # CONFIRMATION HANDLER
    # ==================================================

    def _handle_confirmation(self, message):

        normalized = message.lower()

        # --------------------------------------------------
        # CONFIRM
        # --------------------------------------------------

        if normalized in {
            "yes",
            "y",
            "confirm",
            "confirmed",
            "record it",
        }:

            transaction = self.pending_transaction
            connection = get_connection()

            try:

                create_transaction(
                    connection=connection,
                    account_id=self.account_id,
                    amount=transaction["amount"],
                    transaction_type=transaction["transaction_type"],
                    category=transaction["category"],
                    merchant=transaction["merchant"],
                    description=transaction["description"],
                    source="manual",
                    status="confirmed",
                )

                financial_state = calculate_financial_state(
                    connection
                )

                decisions = evaluate_financial_state(
                    financial_state
                )

            finally:

                connection.close()

            self.pending_transaction = None
            self.state = "IDLE"

            response = (
                "✅ Transaction recorded.\n\n"
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

        # --------------------------------------------------
        # REJECT
        # --------------------------------------------------

        if normalized in {
            "no",
            "n",
            "cancel",
            "discard",
        }:

            self.pending_transaction = None
            self.state = "IDLE"

            return "Transaction discarded."

        # --------------------------------------------------
        # UNKNOWN CONFIRMATION
        # --------------------------------------------------

        return (
            "Please confirm the transaction with "
            "**yes** or **no**."
        )

    # ==================================================
    # FINANCIAL QUERIES
    # ==================================================

    def _handle_financial_query(self, query_type):

        connection = get_connection()

        try:

            financial_state = calculate_financial_state(
                connection
            )

        finally:

            connection.close()

        # --------------------------------------------------
        # CURRENT BALANCE
        # --------------------------------------------------

        if query_type == "current_balance":

            return (
                f"Your current balance is "
                f"₹{financial_state.current_balance:,.2f}."
            )

        # --------------------------------------------------
        # SPENDABLE BALANCE
        # --------------------------------------------------

        if query_type == "spendable_balance":

            return (
                f"You currently have "
                f"₹{financial_state.spendable_balance:,.2f} "
                f"available to spend."
            )

        # --------------------------------------------------
        # FINANCIAL SUMMARY
        # --------------------------------------------------

        if query_type == "financial_summary":

            return (
                f"Current balance: "
                f"₹{financial_state.current_balance:,.2f}\n\n"
                f"Spendable balance: "
                f"₹{financial_state.spendable_balance:,.2f}"
            )

        # --------------------------------------------------
        # NOT IMPLEMENTED YET
        # --------------------------------------------------

        if query_type == "upcoming_commitments":

            return (
                "Upcoming commitment details "
                "aren't available yet."
            )

        if query_type == "savings":

            return (
                "Savings details aren't available yet."
            )

        return (
            "I couldn't determine which financial "
            "information you wanted."
        )

    # ==================================================
    # SPENDING QUERIES
    # ==================================================

    def _handle_spending_query(self, message):

        return (
            "Spending analysis isn't available yet."
        )