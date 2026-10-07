import streamlit as st
import pandas as pd
import html

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

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if "last_results" not in st.session_state:
    st.session_state.last_results = []


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 15%, rgba(86, 70, 255, 0.12), transparent 30%),
        radial-gradient(circle at 85% 80%, rgba(0, 210, 255, 0.08), transparent 30%),
        #070912;
    color: #f4f5f7;
}

/* Hide Streamlit default elements */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* ============================================================
   LOGIN PAGE
   ============================================================ */

.login-wrapper {
    min-height: 85vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.login-card {
    width: 440px;
    padding: 45px;
    border-radius: 25px;

    background: rgba(18, 21, 34, 0.86);
    border: 1px solid rgba(255,255,255,0.09);

    box-shadow:
        0 25px 80px rgba(0,0,0,0.55),
        0 0 50px rgba(90,70,255,0.08);

    backdrop-filter: blur(20px);
}

.logo {
    width: 70px;
    height: 70px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin: 0 auto 20px auto;

    border-radius: 20px;

    background: linear-gradient(
        135deg,
        #6d5dfc,
        #00c6ff
    );

    font-size: 30px;
    font-weight: 700;

    box-shadow: 0 10px 35px rgba(72, 85, 255, 0.35);
}

.login-title {
    text-align: center;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 31px;
    font-weight: 700;
    margin-bottom: 8px;
}

.login-subtitle {
    text-align: center;
    color: #9298aa;
    font-size: 14px;
    margin-bottom: 30px;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background: #0b0e18;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.sidebar-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 21px;
    font-weight: 700;
    margin-bottom: 5px;
}

.sidebar-subtitle {
    color: #777e92;
    font-size: 12px;
    margin-bottom: 30px;
}

.user-card {
    padding: 15px;
    border-radius: 15px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 25px;
}

.avatar {
    width: 38px;
    height: 38px;

    display: inline-flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background: linear-gradient(
        135deg,
        #6d5dfc,
        #00c6ff
    );

    font-weight: 700;
}


/* ============================================================
   MAIN HEADER
   ============================================================ */

.main-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 10px 0 25px 0;
}

.main-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 29px;
    font-weight: 700;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 8px;

    padding: 7px 13px;

    border-radius: 30px;

    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.15);

    color: #71e89b;
    font-size: 12px;
}

.status-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #4ade80;

    box-shadow: 0 0 10px #4ade80;
}


/* ============================================================
   WELCOME CARD
   ============================================================ */

.welcome-card {
    padding: 28px;

    border-radius: 22px;

    background:
        linear-gradient(
            135deg,
            rgba(109,93,252,0.13),
            rgba(0,198,255,0.05)
        );

    border: 1px solid rgba(255,255,255,0.08);

    margin-bottom: 25px;
}

.welcome-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 23px;
    font-weight: 600;
}

.welcome-text {
    color: #979daf;
    font-size: 14px;
    line-height: 1.6;
}


/* ============================================================
   CHAT
   ============================================================ */

.user-message {
    display: flex;
    justify-content: flex-end;
    margin: 20px 0;
}

.user-bubble {
    max-width: 75%;

    padding: 14px 18px;

    border-radius: 18px 18px 4px 18px;

    background: linear-gradient(
        135deg,
        #635bdb,
        #4c70df
    );

    color: white;

    font-size: 14px;
    line-height: 1.5;

    box-shadow: 0 10px 30px rgba(76,112,223,0.18);
}

.ai-message {
    display: flex;
    gap: 13px;

    margin: 20px 0;
}

.ai-avatar {
    flex-shrink: 0;

    width: 38px;
    height: 38px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 12px;

    background: linear-gradient(
        135deg,
        #6d5dfc,
        #00c6ff
    );

    font-weight: 700;
}

.ai-content {
    max-width: 85%;

    padding: 15px 18px;

    border-radius: 5px 18px 18px 18px;

    background: rgba(255,255,255,0.045);

    border: 1px solid rgba(255,255,255,0.07);

    color: #dfe2e9;

    font-size: 14px;

    line-height: 1.65;
}


/* ============================================================
   RESULT CARD
   ============================================================ */

.result-card {
    margin: 18px 0 25px 51px;

    padding: 20px;

    border-radius: 18px;

    background: rgba(255,255,255,0.025);

    border: 1px solid rgba(255,255,255,0.07);
}

.result-title {
    font-family: 'Space Grotesk', sans-serif;

    font-size: 15px;
    font-weight: 600;

    margin-bottom: 15px;
}

.result-count {
    color: #858ca0;
    font-size: 12px;
    margin-bottom: 12px;
}


/* ============================================================
   FOLLOW UP
   ============================================================ */

.follow-title {
    color: #858ca0;

    font-size: 12px;

    margin-top: 25px;
    margin-bottom: 10px;

    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.follow-card {
    padding: 13px 16px;

    border-radius: 13px;

    background: rgba(255,255,255,0.035);

    border: 1px solid rgba(255,255,255,0.06);

    color: #c7cbd5;

    font-size: 13px;
}


/* ============================================================
   INPUT
   ============================================================ */

div[data-testid="stTextInput"] input {
    background: #111522 !important;

    border: 1px solid rgba(255,255,255,0.10) !important;

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


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    border-radius: 12px;

    border: 1px solid rgba(255,255,255,0.08);

    background: rgba(255,255,255,0.05);

    color: #e9ebef;

    font-weight: 500;

    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: #6d5dfc;

    background: rgba(109,93,252,0.14);

    color: white;
}

.login-button .stButton > button {
    width: 100%;

    background: linear-gradient(
        135deg,
        #6d5dfc,
        #4779ef
    );

    border: none;

    color: white;

    padding: 10px;

    font-weight: 600;

    box-shadow:
        0 10px 25px rgba(78,94,230,0.25);
}


/* ============================================================
   SQL BOX
   ============================================================ */

.sql-box {
    margin: 15px 0;

    padding: 16px;

    border-radius: 14px;

    background: #080b12;

    border: 1px solid rgba(255,255,255,0.06);

    font-family: monospace;

    font-size: 12px;

    color: #aeb6c9;

    overflow-x: auto;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {
    text-align: center;

    color: #555b6c;

    font-size: 11px;

    margin-top: 45px;

    padding-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.markdown("""
    <div class="login-wrapper">
        <div class="login-card">

            <div class="logo">◈</div>

            <div class="login-title">
                AI Database Assistant
            </div>

            <div class="login-subtitle">
                Ask questions. Explore data. Get intelligent answers.
            </div>

        </div>
    </div>
    """, unsafe_allow_html=True)

    # Put actual login controls underneath the HTML card
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        st.markdown('<div class="login-button">', unsafe_allow_html=True)

        if st.button("Sign In", use_container_width=True):

            # ------------------------------------------------
            # SIMPLE DEMO LOGIN
            # Change these credentials later.
            # ------------------------------------------------

            if username == "admin" and password == "admin123":

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:

                st.error("Invalid username or password.")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="footer">
            Natural Language → SQL → Database → AI Answer
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# FOLLOW-UP QUESTION GENERATOR
# ============================================================

def get_follow_up_questions(question):

    q = question.lower()

    if "employee" in q and "department" in q:
        return [
            "Which department has the most employees?",
            "Show the average salary of each department.",
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
        st.info("The query returned no results.")
        return

    # Convert tuples/lists to DataFrame

    df = pd.DataFrame(results)

    # Create generic column names
    if all(str(col).isdigit() for col in df.columns):
        df.columns = [
            f"Column {i + 1}"
            for i in range(len(df.columns))
        ]

    st.markdown(
        f"""
        <div class="result-card">

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
# MAIN APPLICATION
# ============================================================

def main_app():

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-logo">
                ◈ AI Database
            </div>

            <div class="sidebar-subtitle">
                Natural Language Database Assistant
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="user-card">

                <div class="avatar">
                    {st.session_state.username[:1].upper()}
                </div>

                <div style="display:inline-block; margin-left:10px;">
                    <div style="font-size:13px; font-weight:600;">
                        {html.escape(st.session_state.username)}
                    </div>

                    <div style="font-size:11px; color:#777e92;">
                        Database User
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("＋  New Conversation", use_container_width=True):

            st.session_state.messages = []
            st.session_state.last_question = ""
            st.session_state.last_answer = ""
            st.session_state.last_results = []

            st.rerun()

        st.markdown("###")

        st.markdown(
            """
            <div style="
                color:#737a8e;
                font-size:11px;
                text-transform:uppercase;
                letter-spacing:.08em;
                margin-bottom:10px;
            ">
                Suggested
            </div>
            """,
            unsafe_allow_html=True
        )

        suggestions = [
            "How many employees are there?",
            "Show the top 5 salaries",
            "Show employees and their departments",
            "Show countries and regions"
        ]

        for suggestion in suggestions:

            if st.button(
                suggestion,
                key="side_" + suggestion,
                use_container_width=True
            ):

                st.session_state.last_question = suggestion

        st.markdown("---")

        if st.button("Logout", use_container_width=True):

            st.session_state.logged_in = False
            st.session_state.username = ""

            st.rerun()

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="main-header">

            <div>
                <div class="main-title">
                    Database Assistant
                </div>

                <div style="
                    color:#747b8e;
                    font-size:13px;
                    margin-top:4px;
                ">
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

    # --------------------------------------------------------
    # WELCOME
    # --------------------------------------------------------

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="welcome-card">

                <div class="welcome-title">
                    👋 Welcome to your AI Database Assistant
                </div>

                <div class="welcome-text">
                    Ask questions about your database using normal
                    language. I'll translate your question into SQL,
                    execute it, and explain the results for you.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    for message in st.session_state.messages:

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

            st.markdown(
                f"""
                <div class="ai-message">

                    <div class="ai-avatar">
                        AI
                    </div>

                    <div class="ai-content">
                        {html.escape(message["content"]).replace(chr(10), "<br>")}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            if message.get("results"):

                display_results(message["results"])

                # --------------------------------------------
                # FOLLOW-UP QUESTIONS
                # --------------------------------------------

                st.markdown(
                    """
                    <div class="follow-title">
                        You might also ask
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                followups = message.get("followups", [])

                cols = st.columns(len(followups))

                for i, followup in enumerate(followups):

                    with cols[i]:

                        if st.button(
                            followup,
                            key=f"follow_{len(st.session_state.messages)}_{i}",
                            use_container_width=True
                        ):

                            st.session_state.last_question = followup

    # --------------------------------------------------------
    # QUESTION INPUT
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    question = st.text_input(
        "Ask your database",
        value=st.session_state.last_question,
        placeholder="e.g. Show the top 5 employees with the highest salaries",
        label_visibility="collapsed"
    )

    col1, col2, col3 = st.columns([1, 5, 1])

    with col2:

        ask = st.button(
            "✦  Ask Database",
            use_container_width=True
        )

    if ask and question.strip():

        question = question.strip()

        # Clear previous automatically selected question
        st.session_state.last_question = ""

        # ----------------------------------------------------
        # ADD USER MESSAGE
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        # ----------------------------------------------------
        # BACKEND
        # ----------------------------------------------------

        with st.spinner("Understanding your question..."):

            try:

                # =================================================
                # USE YOUR EXISTING BACKEND FUNCTIONS HERE
                # =================================================

                sql, relevant_schema = generate_sql(question)

                # SQL validation
                validation_result = validate_sql(
                    sql,
                    relevant_schema
                )

                if not validation_result:

                    raise Exception(
                        "Generated SQL failed validation."
                    )

                # Execute SQL
                results = execute_sql(sql)

                # Generate AI answer
                answer = generate_answer(
                    question,
                    results
                )

                # =================================================
                # STORE RESPONSE
                # =================================================

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "results": results,
                        "sql": sql,
                        "followups": get_follow_up_questions(question)
                    }
                )

            except Exception as e:

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content":
                            "I couldn't process that question. "
                            f"Error: {str(e)}",
                        "results": [],
                        "followups": []
                    }
                )

        st.rerun()

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="footer">
            Natural Language to SQL • AI-Assisted Database Query System
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# APPLICATION ROUTER
# ============================================================

if not st.session_state.logged_in:

    login_page()

else:

    main_app()