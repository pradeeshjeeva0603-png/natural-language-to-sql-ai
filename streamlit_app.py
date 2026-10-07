import streamlit as st
import pandas as pd
import html

from app import (
    generate_sql,
    execute_sql,
    generate_answer,
    fix_sql
)

from sql_validator import validate_sql
from schema import JOIN_RELATIONSHIPS


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Database Assistant",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "question_input" not in st.session_state:
    st.session_state.question_input = ""


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');


/* ==========================================================
   GLOBAL
   ========================================================== */

* {
    font-family: 'Inter', sans-serif;
}

.stApp {

    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(99, 91, 219, 0.15),
            transparent 30%
        ),

        radial-gradient(
            circle at 90% 85%,
            rgba(0, 198, 255, 0.08),
            transparent 30%
        ),

        #070912;

    color: #f5f5f7;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* ==========================================================
   LOGIN
   ========================================================== */

.login-container {

    max-width: 460px;

    margin: 8vh auto 0 auto;

    padding: 45px;

    border-radius: 25px;

    background: rgba(17, 20, 32, 0.88);

    border: 1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 30px 90px rgba(0,0,0,0.55),
        0 0 60px rgba(99,91,219,0.08);

    backdrop-filter: blur(20px);
}


.logo {

    width: 72px;
    height: 72px;

    margin: 0 auto 22px auto;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 20px;

    background:
        linear-gradient(
            135deg,
            #6d5dfc,
            #00c6ff
        );

    font-size: 31px;
    font-weight: 700;

    box-shadow:
        0 12px 35px rgba(80,90,240,0.3);
}


.login-title {

    text-align: center;

    font-family: 'Space Grotesk', sans-serif;

    font-size: 30px;

    font-weight: 700;

    margin-bottom: 8px;
}


.login-subtitle {

    text-align: center;

    color: #8f96a9;

    font-size: 14px;

    line-height: 1.6;

    margin-bottom: 30px;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {

    background: #0b0e18;

    border-right:
        1px solid rgba(255,255,255,0.06);
}


.sidebar-title {

    font-family: 'Space Grotesk', sans-serif;

    font-size: 21px;

    font-weight: 700;
}


.sidebar-subtitle {

    color: #70778b;

    font-size: 11px;

    margin-top: 4px;

    margin-bottom: 28px;
}


.user-card {

    padding: 14px;

    border-radius: 15px;

    background: rgba(255,255,255,0.035);

    border:
        1px solid rgba(255,255,255,0.06);

    margin-bottom: 20px;
}


.avatar {

    width: 38px;
    height: 38px;

    display: inline-flex;

    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background:
        linear-gradient(
            135deg,
            #6d5dfc,
            #00c6ff
        );

    font-weight: 700;
}


/* ==========================================================
   HEADER
   ========================================================== */

.main-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    margin-bottom: 25px;
}


.main-title {

    font-family: 'Space Grotesk', sans-serif;

    font-size: 29px;

    font-weight: 700;
}


.main-subtitle {

    color: #747b8e;

    font-size: 13px;

    margin-top: 4px;
}


.status {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    padding: 7px 13px;

    border-radius: 30px;

    background: rgba(34,197,94,0.08);

    border:
        1px solid rgba(34,197,94,0.15);

    color: #71e89b;

    font-size: 11px;
}


.status-dot {

    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #4ade80;

    box-shadow: 0 0 10px #4ade80;
}


/* ==========================================================
   WELCOME
   ========================================================== */

.welcome-card {

    padding: 28px;

    border-radius: 22px;

    background:
        linear-gradient(
            135deg,
            rgba(109,93,252,0.13),
            rgba(0,198,255,0.04)
        );

    border:
        1px solid rgba(255,255,255,0.07);

    margin-bottom: 28px;
}


.welcome-title {

    font-family: 'Space Grotesk', sans-serif;

    font-size: 22px;

    font-weight: 600;

    margin-bottom: 8px;
}


.welcome-text {

    color: #969daf;

    font-size: 13px;

    line-height: 1.7;
}


/* ==========================================================
   CHAT
   ========================================================== */

.user-message {

    display: flex;

    justify-content: flex-end;

    margin:
        18px 0;
}


.user-bubble {

    max-width: 72%;

    padding: 13px 17px;

    border-radius:
        18px 18px 4px 18px;

    background:
        linear-gradient(
            135deg,
            #635bdb,
            #4c70df
        );

    color: white;

    font-size: 14px;

    line-height: 1.5;

    box-shadow:
        0 10px 30px rgba(76,112,223,0.16);
}


.ai-message {

    display: flex;

    gap: 12px;

    margin:
        18px 0;
}


.ai-avatar {

    flex-shrink: 0;

    width: 38px;
    height: 38px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 12px;

    background:
        linear-gradient(
            135deg,
            #6d5dfc,
            #00c6ff
        );

    font-size: 11px;

    font-weight: 700;
}


.ai-content {

    max-width: 85%;

    padding: 15px 18px;

    border-radius:
        5px 18px 18px 18px;

    background:
        rgba(255,255,255,0.045);

    border:
        1px solid rgba(255,255,255,0.07);

    color: #dfe2e9;

    font-size: 14px;

    line-height: 1.65;
}


/* ==========================================================
   SQL
   ========================================================== */

.sql-container {

    margin:
        10px 0 18px 50px;

    padding: 15px;

    border-radius: 14px;

    background: #080b12;

    border:
        1px solid rgba(255,255,255,0.06);
}


.sql-label {

    color: #70778b;

    font-size: 10px;

    text-transform: uppercase;

    letter-spacing: 0.1em;

    margin-bottom: 8px;
}


.sql-code {

    color: #aeb6c9;

    font-family: monospace;

    font-size: 12px;

    line-height: 1.6;

    overflow-x: auto;
}


/* ==========================================================
   RESULTS
   ========================================================== */

.result-container {

    margin:
        10px 0 20px 50px;

    padding: 20px;

    border-radius: 18px;

    background:
        rgba(255,255,255,0.025);

    border:
        1px solid rgba(255,255,255,0.07);
}


.result-title {

    font-family: 'Space Grotesk', sans-serif;

    font-size: 15px;

    font-weight: 600;

    margin-bottom: 5px;
}


.result-count {

    color: #747b8e;

    font-size: 11px;

    margin-bottom: 12px;
}


/* ==========================================================
   FOLLOW UPS
   ========================================================== */

.follow-title {

    color: #70778b;

    font-size: 10px;

    text-transform: uppercase;

    letter-spacing: 0.1em;

    margin:
        22px 0 10px 50px;
}


/* ==========================================================
   INPUT
   ========================================================== */

div[data-testid="stTextInput"] input {

    background: #111522 !important;

    border:
        1px solid rgba(255,255,255,0.10) !important;

    border-radius: 14px !important;

    color: white !important;

    padding: 14px !important;
}


div[data-testid="stTextInput"] input:focus {

    border-color: #6d5dfc !important;

    box-shadow:
        0 0 0 1px #6d5dfc,
        0 0 20px rgba(109,93,252,0.15) !important;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {

    border-radius: 12px;

    border:
        1px solid rgba(255,255,255,0.08);

    background:
        rgba(255,255,255,0.045);

    color: #e9ebef;

    font-weight: 500;

    transition:
        all 0.2s ease;
}


.stButton > button:hover {

    border-color: #6d5dfc;

    background:
        rgba(109,93,252,0.14);

    color: white;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.footer {

    text-align: center;

    color: #4f5566;

    font-size: 10px;

    margin-top: 40px;

    padding-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FOLLOW-UP QUESTIONS
# ============================================================

def get_followups(question):

    q = question.lower()

    if "employee" in q and "department" in q:

        return [
            "Which department has the most employees?",
            "Show the average salary by department.",
            "Show the highest paid employee in each department."
        ]

    if "salary" in q:

        return [
            "Who is the highest paid employee?",
            "Show the average salary by department.",
            "Show the top 5 highest paid employees."
        ]

    if "department" in q:

        return [
            "How many employees are in each department?",
            "Show the cities of all departments.",
            "Which department has the highest average salary?"
        ]

    if "job" in q:

        return [
            "Show all available job titles.",
            "Show employees and their current jobs.",
            "Show the previous jobs of employees."
        ]

    if "country" in q:

        return [
            "Show the countries and their regions.",
            "Show the locations in each country.",
            "How many departments are in each country?"
        ]

    return [
        "How many employees are there?",
        "Show the top 5 highest paid employees.",
        "Show all departments and their cities."
    ]


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(results):

    if not results:
        st.info("No results found.")
        return

    df = pd.DataFrame(results)

    st.markdown(
        f"""
        <div class="result-container">

            <div class="result-title">
                📊 Query Results
            </div>

            <div class="result-count">
                {len(results)} result(s) found
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# LOGIN PAGE
# ============================================================

def show_login():

    st.markdown(
        """
        <div class="login-container">

            <div class="logo">
                ◈
            </div>

            <div class="login-title">
                AI Database Assistant
            </div>

            <div class="login-subtitle">
                Ask questions. Explore data.
                Get intelligent answers.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:

        username = st.text_input(
            "Username",
            placeholder="Enter username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password"
        )

        if st.button(
            "Sign In",
            use_container_width=True
        ):

            if username == "admin" and password == "admin123":

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

        st.markdown(
            """
            <div class="footer">
                Natural Language → SQL → Database → AI Answer
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# MAIN APPLICATION
# ============================================================

def show_dashboard():

    # ========================================================
    # SIDEBAR
    # ========================================================

    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-title">
                ◈ AI Database
            </div>

            <div class="sidebar-subtitle">
                Natural Language Database Assistant
            </div>
            """,
            unsafe_allow_html=True
        )

        username = html.escape(
            st.session_state.username
        )

        first_letter = username[:1].upper()

        st.markdown(
            f"""
            <div class="user-card">

                <div class="avatar">
                    {first_letter}
                </div>

                <span style="
                    margin-left:10px;
                    font-size:13px;
                    font-weight:600;
                ">
                    {username}
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "＋  New Conversation",
            use_container_width=True
        ):

            st.session_state.messages = []

            st.rerun()

        st.markdown("")

        st.markdown(
            """
            <div style="
                color:#70778b;
                font-size:10px;
                text-transform:uppercase;
                letter-spacing:.1em;
                margin-bottom:10px;
            ">
                Quick Questions
            </div>
            """,
            unsafe_allow_html=True
        )

        quick_questions = [
            "How many employees are there?",
            "Show the top 5 salaries",
            "Show employees and departments",
            "Show countries and regions"
        ]

        for q in quick_questions:

            if st.button(
                q,
                key="quick_" + q,
                use_container_width=True
            ):

                st.session_state.question_input = q

        st.markdown("---")

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False

            st.session_state.username = ""

            st.session_state.messages = []

            st.rerun()


    # ========================================================
    # HEADER
    # ========================================================

    st.markdown(
        """
        <div class="main-header">

            <div>

                <div class="main-title">
                    Database Assistant
                </div>

                <div class="main-subtitle">
                    Ask your database anything in natural language.
                </div>

            </div>

            <div class="status">

                <span class="status-dot"></span>

                Database Connected

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # WELCOME
    # ========================================================

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="welcome-card">

                <div class="welcome-title">
                    👋 Welcome to your AI Database Assistant
                </div>

                <div class="welcome-text">
                    Ask questions using normal language.
                    The system converts your question into SQL,
                    executes it against the database and explains
                    the results using AI.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    for index, message in enumerate(
        st.session_state.messages
    ):

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="user-message">

                    <div class="user-bubble">
                        {html.escape(message["content"])}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            answer = html.escape(
                message["content"]
            ).replace("\n", "<br>")

            st.markdown(
                f"""
                <div class="ai-message">

                    <div class="ai-avatar">
                        AI
                    </div>

                    <div class="ai-content">
                        {answer}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


            # =================================================
            # SQL
            # =================================================

            if message.get("sql"):

                safe_sql = html.escape(
                    message["sql"]
                )

                with st.expander(
                    "View Generated SQL"
                ):

                    st.code(
                        message["sql"],
                        language="sql"
                    )


            # =================================================
            # RESULTS
            # =================================================

            if message.get("results"):

                display_results(
                    message["results"]
                )


            # =================================================
            # FOLLOW-UP QUESTIONS
            # =================================================

            followups = message.get(
                "followups",
                []
            )

            if followups:

                st.markdown(
                    """
                    <div class="follow-title">
                        You might also ask
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                cols = st.columns(
                    len(followups)
                )

                for i, followup in enumerate(
                    followups
                ):

                    with cols[i]:

                        if st.button(
                            followup,
                            key=f"follow_{index}_{i}",
                            use_container_width=True
                        ):

                            st.session_state.question_input = followup

                            st.rerun()


    # ========================================================
    # QUESTION INPUT
    # ========================================================

    st.markdown("<br>", unsafe_allow_html=True)

    question = st.text_input(
        "Ask your database",
        key="question_input",
        placeholder=
            "e.g. Show the top 5 employees with the highest salaries",
        label_visibility="collapsed"
    )


    col1, col2, col3 = st.columns(
        [1, 5, 1]
    )

    with col2:

        ask = st.button(
            "✦  Ask Database",
            use_container_width=True
        )


    # ========================================================
    # PROCESS QUESTION
    # ========================================================

    if ask and question.strip():

        question = question.strip()

        # --------------------------------------------
        # USER MESSAGE
        # --------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # --------------------------------------------
        # GENERATE SQL
        # --------------------------------------------

        with st.spinner(
            "Understanding your question..."
        ):

            sql, relevant_schema = generate_sql(
                question
            )


        # --------------------------------------------
        # VALIDATE SQL
        # --------------------------------------------

        is_valid, validation_message = validate_sql(
            sql
        )

        if not is_valid:

            st.session_state.messages.append(
                {
                    "role": "assistant",

                    "content":
                        "I couldn't safely execute "
                        "the generated query.",

                    "results": [],

                    "sql": sql,

                    "followups": []
                }
            )

            st.rerun()


        # --------------------------------------------
        # EXECUTE SQL
        # --------------------------------------------

        with st.spinner(
            "Querying the database..."
        ):

            results, error = execute_sql(
                sql
            )


        # --------------------------------------------
        # ERROR RECOVERY
        # --------------------------------------------

        if error:

            with st.spinner(
                "Fixing the SQL query..."
            ):

                fixed_sql = fix_sql(
                    sql,
                    error,
                    question,
                    relevant_schema,
                    JOIN_RELATIONSHIPS
                )


            fixed_valid, fixed_message = validate_sql(
                fixed_sql
            )


            if fixed_valid:

                results, error = execute_sql(
                    fixed_sql
                )

                if not error:

                    sql = fixed_sql


        # --------------------------------------------
        # FINAL ERROR
        # --------------------------------------------

        if error:

            answer = (
                "I couldn't execute the generated "
                "query. Please try rephrasing "
                "your question."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",

                    "content": answer,

                    "results": [],

                    "sql": sql,

                    "followups": []
                }
            )

            st.rerun()


        # --------------------------------------------
        # AI ANSWER
        # --------------------------------------------

        with st.spinner(
            "Preparing your answer..."
        ):

            answer = generate_answer(
                question,
                results
            )


        # --------------------------------------------
        # FOLLOW-UP QUESTIONS
        # --------------------------------------------

        followups = get_followups(
            question
        )


        # --------------------------------------------
        # STORE EVERYTHING
        # --------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",

                "content": answer,

                "results": results,

                "sql": sql,

                "followups": followups
            }
        )


        st.rerun()


    # ========================================================
    # FOOTER
    # ========================================================

    st.markdown(
        """
        <div class="footer">
            Natural Language to SQL •
            AI-Assisted Database Query System
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# APP ROUTER
# ============================================================

if st.session_state.logged_in:

    show_dashboard()

else:

    show_login()