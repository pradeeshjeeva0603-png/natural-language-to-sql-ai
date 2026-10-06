from ollama import chat
from database import get_connection
from vector_retriever import retrieve_schema
from sql_validator import validate_sql
from schema import JOIN_RELATIONSHIPS


def generate_sql(question):
    relevant_schema, relevant_tables = retrieve_schema(question)

    history_requested = any(word in question.lower() for word in [
        "history",
        "previous job",
        "past job",
        "employment history",
        "previous department",
        "past department"
    ])

    if not history_requested:
        relevant_schema = "\n".join(
            block for block in relevant_schema.split("\n\n\n")
            if not block.startswith("TABLE: job_history")
        )

    prompt = f"""
You are a MySQL Text-to-SQL assistant.

Your job is to convert a natural language question into ONE correct MySQL SELECT query.

RELEVANT DATABASE SCHEMA:
{relevant_schema}

VALID JOIN RELATIONSHIPS:
{JOIN_RELATIONSHIPS}

IMPORTANT RULES:

1. Use ONLY tables and columns that appear in the RELEVANT DATABASE SCHEMA above.
2. NEVER use a table that is not present in the RELEVANT DATABASE SCHEMA.
3. A foreign-key relationship shown in the schema does NOT mean you must join that table.
4. Join a table ONLY when the user's question requires a column or filter from that table.
5. Always use the shortest possible JOIN path needed to answer the question.
6. Do NOT add extra tables just because they are related through foreign keys.
7. Do NOT follow foreign-key relationships beyond what is required by the question.
8. If the question asks for department names and cities, use only departments and locations.
    8.1. If the user asks for cities, SELECT the CITY column, not LOCATION_ID.
    8.2. If the user asks for department names and cities, the SELECT clause must contain DEPARTMENT_NAME and CITY.
    8.3. Never SELECT a foreign key such as LOCATION_ID when the user asks for the information represented by that foreign key.
    8.4. When two joined tables contain a column with the same name, always qualify the column with its table name.
9. If the question asks for employees and job titles, use employees and jobs, plus departments only when department information is requested.
10. Do NOT use job_history unless the question specifically asks about employment history, previous jobs, past jobs, or past departments.
11. Do NOT join locations, countries, or regions unless the question requires location, city, country, or region information.
12. Never invent tables, columns, or relationships.
13. Use ONLY tables and columns explicitly present in the RELEVANT DATABASE SCHEMA.
14. Do NOT use tables or columns merely because they appear in VALID JOIN RELATIONSHIPS.
15. Return ONLY the SQL query.
16. Do not use markdown.
17. Do not explain the answer.

EXAMPLES:

Question:
Who is the highest paid employee?

SQL:
SELECT FIRST_NAME, LAST_NAME, SALARY
FROM employees
ORDER BY SALARY DESC
LIMIT 1;

Question:
Show the top 5 employees with the highest salaries.

SQL:
SELECT FIRST_NAME, LAST_NAME, SALARY
FROM employees
ORDER BY SALARY DESC
LIMIT 5;

Question:
How many employees are there?

SQL:
SELECT COUNT(*) AS employee_count
FROM employees;

Question:
Show the names of all departments and the cities where they are located.

SQL:
SELECT departments.DEPARTMENT_NAME, locations.CITY
FROM departments
JOIN locations
ON departments.LOCATION_ID = locations.LOCATION_ID;

FINAL INSTRUCTION:

Before generating SQL, identify the minimum tables required to answer the question.

You MUST use ONLY those tables.

Do NOT add a table merely because:
- it is referenced by a foreign key,
- it is related to another table,
- it appears in a foreign-key description,
- or it could provide additional information.

For this question, if the answer can be obtained using two tables, use exactly those two tables.

The generated SQL must not reference any table that is not necessary to answer the user's question.

NOW CONVERT THIS QUESTION:

Question:
{question}

SQL:
"""

    response = chat(
        model="mohamedelawakey/sql_coder",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip(), relevant_schema

def execute_sql(sql):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        return results, None

    except Exception as e:
        return None, str(e)

    finally:
        cursor.close()
        connection.close()
def generate_answer(question, results):
    prompt = f"""
You are an AI database assistant.

Answer the user's question using ONLY the database results provided below.

USER QUESTION:
{question}

DATABASE RESULTS:
{results}

RULES:
1. Answer the user's original question directly.
2. Use only information present in the database results.
3. Do not invent or assume any information.
4. Do not mention SQL, tables, queries, schemas, or database errors.
5. If there are many rows, summarize them instead of listing every row.
6. Keep the answer concise and easy to understand.
7. Return only the natural-language answer.
"""

    response = chat(
        model="mohamedelawakey/sql_coder",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"].strip()

def fix_sql(sql, error, question, relevant_schema, join_relationships):
    prompt = f"""
You are an expert MySQL SQL debugger.

Your task is to generate a completely NEW SQL query that correctly answers the original user's question.

ORIGINAL USER QUESTION:
{question}

RELEVANT DATABASE SCHEMA:
{relevant_schema}

VALID JOIN RELATIONSHIPS:
{join_relationships}

PREVIOUS FAILED SQL:
{sql}

MYSQL ERROR:
{error}

IMPORTANT RULES:
1. Ignore the previous SQL and generate the query from scratch.
2. Answer ONLY the original user's question.
3. Use ONLY tables and columns that exist in the provided schema.
4. Use the minimum number of tables required to answer the question.
5. Join a table only when its columns or data are required by the question.
6. Do not add unnecessary columns to the SELECT clause.
7. Do not add unnecessary JOINs or WHERE conditions.
8. Do not invent tables, columns, or relationships.
9. Follow the valid JOIN relationships provided in the schema.
10. If multiple tables are required, use the shortest valid JOIN path.
11. Preserve the meaning and intent of the original question.
12. Return ONLY one valid MySQL SELECT query.
13. Use ONLY tables and columns explicitly present in the RELEVANT DATABASE SCHEMA.
14. Do NOT use tables or columns merely because they appear in VALID JOIN RELATIONSHIPS.
15. Do not use markdown.
16. Do not explain the answer.
17. Every JOIN condition MUST exactly follow one of the VALID JOIN RELATIONSHIPS provided above.
18. NEVER create a JOIN condition using columns that are not connected by a VALID JOIN RELATIONSHIP.

Generate the corrected SQL query now:
"""

    response = chat(
        model="mohamedelawakey/sql_coder",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"].strip()


def main():
    print("======================================")
    print("   AI DATABASE ASSISTANT")
    print("======================================")

    question = input("\nAsk a question about the database: ")

    print("\nGenerating SQL...\n")

    sql, relevant_schema = generate_sql(question)

    print("Generated SQL:")
    print(sql)


    is_valid, message = validate_sql(sql)

    print("\nSQL Validation:")
    print(message)

    if not is_valid:
        print("\nQuery rejected for safety.")
        return

    print("\nExecuting SQL...")

    results, error = execute_sql(sql)

    if error:
        print("\nSQL Execution Error:")
        print(error)

        print("\nAttempting to fix SQL...")

        fixed_sql = fix_sql(sql, error, question, relevant_schema, JOIN_RELATIONSHIPS)

        print("\nFixed SQL:")
        print(fixed_sql)

        valid, message = validate_sql(fixed_sql)

        if not valid:
            print("\nFixed SQL Validation Error:")
            print(message)
            return

        print("\nExecuting fixed SQL...")

        results, error = execute_sql(fixed_sql)

        if error:
            print("\nFixed SQL Execution Error:")
            print(error)
            return

    print("\nResults:")
    for row in results:
        print(row)
    print("\nAI Answer:")
    answer = generate_answer(question, results)
    print(answer)


if __name__ == "__main__":
    main()