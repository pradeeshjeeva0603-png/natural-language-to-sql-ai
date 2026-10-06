import streamlit as st

from app import generate_sql, execute_sql, fix_sql
from sql_validator import validate_sql


st.set_page_config(
    page_title="AI Database Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Database Assistant")
st.write("Natural Language → SQL → Database Results")

st.divider()

question = st.text_area(
    "Ask a question about the database:",
    placeholder="Example: Show the top 5 employees with the highest salaries.",
    height=100
)

if st.button("🔍 Generate SQL", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:

        with st.spinner("Generating SQL..."):

            sql, relevant_schema = generate_sql(question)

        st.subheader("Generated SQL")
        st.code(sql, language="sql")

        # Validate SQL
        valid, message = validate_sql(sql)

        if not valid:
            st.error("SQL Validation Failed")
            st.write(message)

        else:
            st.success("SQL Validation Passed")

            # Execute SQL
            with st.spinner("Executing SQL..."):

                results, error = execute_sql(sql)

            # If SQL fails
            if error:

                st.error("SQL Execution Error")
                st.code(error)

                st.info("Attempting to automatically fix the SQL...")

                with st.spinner("Fixing SQL..."):

                    fixed_sql = fix_sql(
                        sql,
                        error,
                        question,
                        relevant_schema
                    )

                st.subheader("Fixed SQL")
                st.code(fixed_sql, language="sql")

                # Validate fixed SQL
                valid, message = validate_sql(fixed_sql)

                if not valid:

                    st.error("Fixed SQL Validation Failed")
                    st.write(message)

                else:

                    st.success("Fixed SQL Validation Passed")

                    with st.spinner("Executing fixed SQL..."):

                        results, error = execute_sql(fixed_sql)

                    if error:

                        st.error("Fixed SQL Execution Error")
                        st.code(error)

                    else:

                        st.subheader("Query Results")

                        if results:
                            st.dataframe(results)
                        else:
                            st.info("No results found.")

            else:

                st.subheader("Query Results")

                if results:
                    st.dataframe(results)
                else:
                    st.info("No results found.")