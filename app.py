import streamlit as st

from database.db import get_connection, initialize_database
from core.conversation import ConversationController


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="FinSight",
    page_icon="💰",
    layout="wide",
)


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

initialize_database()
connection = get_connection()


# --------------------------------------------------
# LOAD DEMO USER
# --------------------------------------------------

cursor = connection.execute(
    """
    SELECT id, name
    FROM users
    LIMIT 1
    """
)

user = cursor.fetchone()

if user is None:

    st.error(
        "No user found. Run the demo seed first:\n\n"
        "python3 -m database.seed"
    )

    st.stop()


user_id = user[0]
user_name = user[1]


# --------------------------------------------------
# LOAD ACCOUNT
# --------------------------------------------------

cursor = connection.execute(
    """
    SELECT id, name
    FROM accounts
    WHERE user_id = ?
    LIMIT 1
    """,
    (user_id,),
)

account = cursor.fetchone()

if account is None:

    st.error("No financial account found.")

    st.stop()


account_id = account[0]

connection.close()

# --------------------------------------------------
# CONTROLLER
# --------------------------------------------------

if "controller" not in st.session_state:

    st.session_state.controller = ConversationController(
        account_id=account_id,
    )


controller = st.session_state.controller


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("💰 FinSight")

st.caption(
    f"Personal financial assistant · {user_name}"
)


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_message = st.chat_input(
    "Tell me about a transaction..."
)


if user_message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_message)


    response = controller.handle_message(
        user_message
    )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )


    with st.chat_message("assistant"):
        st.markdown(response)