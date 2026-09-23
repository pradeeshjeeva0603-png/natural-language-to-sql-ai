from ollama import chat
from database import get_connection
from schema import DATABASE_SCHEMA
from sql_validator import validate_sql


def generate_sql(question):
    prompt = f"""
    You are a MySQL Text-to-SQL assistant.

    Your job is to convert a natural language question into ONE correct MySQL SELECT query.

    DATABASE SCHEMA:
    {DATABASE_SCHEMA}

    IMPORTANT RULES:
    1. Use ONLY tables and columns that exist in the schema.
    2. Never invent columns, tables, or conditions.
    3. For "highest paid employee", return the employee's first name,
    last name, and salary.
    4. Do not add a manager condition unless the user explicitly asks about managers.
    5. Return ONLY the SQL query.
    6. Do not use markdown.
    7. Do not explain the answer.

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

    return response["message"]["content"].strip()

def execute_sql(sql):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


def main():
    print("======================================")
    print("   AI DATABASE ASSISTANT")
    print("======================================")

    question = input("\nAsk a question about the database: ")

    print("\nGenerating SQL...\n")

    sql = generate_sql(question)

    print("Generated SQL:")
    print(sql)

    is_valid, message = validate_sql(sql)

    print("\nSQL Validation:")
    print(message)

    if not is_valid:
        print("\nQuery rejected for safety.")
        return

    print("\nExecuting SQL...")

    results = execute_sql(sql)

    print("\nResults:")
    for row in results:
        print(row)


if __name__ == "__main__":
    main()