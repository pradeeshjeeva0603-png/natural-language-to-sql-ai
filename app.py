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

1. Use ONLY tables and columns that appear in the RELEVANT DATABASE SCHEMA.
2. NEVER use a table or column that is not present in the RELEVANT DATABASE SCHEMA.
3. Determine exactly what information the user is asking for before generating SQL.
4. Identify the MINIMUM number of tables required to answer the question.
5. Use ONLY those required tables.
6. Do NOT join a table merely because another table has a foreign key referencing it.
7. A foreign-key relationship does NOT mean that the related table must be included.
8. A VALID JOIN RELATIONSHIP may ONLY be used as an ON condition when both tables are actually required and joined.
9. NEVER use a VALID JOIN RELATIONSHIP as a WHERE condition.
10. If a table is not joined in the query, NONE of its columns may appear anywhere in the query.
11. NEVER add a WHERE condition unless the condition is explicitly required by the user's question.
12. NEVER invent filters based on foreign keys, manager relationships, departments, locations, countries, regions, or other schema information.
13. Do NOT add unnecessary JOINs.
14. Do NOT add unnecessary WHERE conditions.
15. Do NOT add unnecessary SELECT columns.
16. Do NOT invent tables, columns, relationships, conditions, or values.
17. Every JOIN condition MUST exactly match one of the VALID JOIN RELATIONSHIPS.
18. NEVER create a JOIN condition by guessing column names or matching similarly named columns.
19. Use the shortest valid JOIN path required to answer the question.
20. When a table is given an alias, ALWAYS use the alias when referring to its columns.
    Never mix the original table name with its alias.
21. If aliases are not necessary, you may avoid aliases entirely.
22. When two tables contain a column with the same name, qualify the column using the table name or alias.
23. If the question asks for information represented by a foreign key, use the referenced table's meaningful column instead of returning the foreign-key ID.
24. If the question asks for department names and cities, use departments and locations only.
    SELECT DEPARTMENT_NAME and CITY.
25. If the question asks for employees and job titles, use employees and jobs.
    Add departments only if department information is explicitly requested.
26. Do NOT use locations, countries, or regions unless the question explicitly requires location, city, country, or region information.
27. Do NOT use job_history unless the question asks about employment history, previous jobs, past jobs, or previous/past departments.

PREVIOUS JOB / EMPLOYMENT HISTORY RULES:
28. When the question asks for previous jobs, past jobs, or employment history, use job_history to identify historical job records.
29. job_history.JOB_ID identifies the historical job.
30. jobs.JOB_ID is the referenced job identifier.
31. jobs.job_title contains the human-readable job title.
32. When previous job titles are requested, connect:
    job_history.JOB_ID = jobs.JOB_ID
33. When previous job titles are requested, SELECT jobs.job_title rather than job_history.JOB_ID.
34. If employee names are explicitly requested along with previous jobs, connect:
    job_history.EMPLOYEE_ID = employees.EMPLOYEE_ID
35. If the question only says "previous jobs of employees" and does NOT explicitly request employee names or employee attributes, do NOT automatically join employees.
36. Do NOT add departments, locations, countries, or regions to a previous-jobs query unless explicitly requested.
37. Do NOT add a WHERE condition to a previous-jobs query unless the user explicitly asks for filtering.

OUTPUT RULES:
38. Return ONLY one valid MySQL SELECT query.
39. Do NOT use markdown.
40. Do NOT explain the query.
41. Do NOT include ```sql or ```.
42. Do NOT generate multiple queries.
43. Before generating SQL, mentally determine:
    a. What information the user wants.
    b. Which table contains that information.
    c. Which additional tables are absolutely required.
    d. Which valid JOIN relationships connect those tables.
    e. Whether any WHERE condition is actually requested.
44. The final query must contain ONLY the tables, columns, joins, and conditions necessary to answer the user's question.

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
    formatted_results = "\n".join(
        f"{i+1}. {row}"
        for i, row in enumerate(results)
    )

    prompt = f"""
You are a helpful AI database assistant.

Answer the user's question using ONLY the database results provided.

USER QUESTION:
{question}

DATABASE RESULTS:
{formatted_results}

IMPORTANT:
- The database results are Python tuples.
- A tuple such as (26,) means the value returned by the query is 26.
- Do not interpret the number of tuples as the answer when the query is an aggregate such as COUNT, SUM, or AVG.
- Use the actual values inside the tuples.
- Do not write SQL.
- Do not mention tables, queries, schemas, or Python.
- Do not invent information.
- Give a short, clear natural-language answer.
- Preserve the exact order of the database results.
- Do not sort, reorder, or rearrange the results.
- When the results are already ordered, keep that order exactly.
- Preserve the exact order of the database results.
- The first result is result 1, the second is result 2, and so on.
- Never reorder or sort the results yourself.
- Use the database results exactly as provided.
- Include all relevant values from every database result row that are needed to answer the user's question.
- Do not omit columns or values that are part of the requested information.

Return ONLY the answer.
"""

    response = chat(
        model="llama3.2:3b",
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

CRITICAL INSTRUCTION:

The PREVIOUS FAILED SQL is incorrect.

DO NOT treat it as a template.

DO NOT repair it.

DO NOT copy its SELECT clause.

DO NOT copy its JOINs.

DO NOT copy its WHERE conditions.

DO NOT copy its filters.

DO NOT preserve its table choices unless they are independently required by the ORIGINAL USER QUESTION.

Reconstruct the query completely from scratch using ONLY:

1. The ORIGINAL USER QUESTION.
2. The RELEVANT DATABASE SCHEMA.
3. The VALID JOIN RELATIONSHIPS.

IMPORTANT RULES:

1. Use ONLY tables and columns that exist in the RELEVANT DATABASE SCHEMA.
2. NEVER use a table or column that does not exist in the RELEVANT DATABASE SCHEMA.
3. Determine exactly what information the ORIGINAL USER QUESTION requests.
4. Identify the MINIMUM number of tables required to answer the question.
5. Use ONLY those required tables.
6. Do NOT add a table merely because it is related through a foreign key.
7. Do NOT add a table merely because it appears in VALID JOIN RELATIONSHIPS.
8. A VALID JOIN RELATIONSHIP may ONLY be used as an ON condition when both tables are actually required and joined.
9. NEVER use a VALID JOIN RELATIONSHIP as a WHERE condition.
10. If a table is not joined in the query, NONE of its columns may appear anywhere in the query.
11. NEVER add a WHERE condition unless it is explicitly required by the ORIGINAL USER QUESTION.
12. NEVER invent filters based on foreign keys, manager relationships, departments, locations, countries, regions, or other schema information.
13. Do NOT add unnecessary JOINs.
14. Do NOT add unnecessary WHERE conditions.
15. Do NOT add unnecessary SELECT columns.
16. Do NOT invent tables, columns, relationships, conditions, or values.
17. Every JOIN condition MUST exactly match one of the VALID JOIN RELATIONSHIPS.
18. NEVER create a JOIN condition by guessing column names or matching similarly named columns.
19. Use the shortest valid JOIN path required to answer the question.
20. When a table is given an alias, ALWAYS use the alias when referring to its columns.
    Never mix the original table name with its alias.
21. If aliases are not necessary, you may avoid aliases entirely.
22. When two tables contain a column with the same name, qualify the column using the table name or alias.
23. If the question asks for information represented by a foreign key, use the referenced table's meaningful column instead of returning the foreign-key ID.
24. Do NOT preserve any unnecessary clause from the PREVIOUS FAILED SQL.
25. Every WHERE condition in the corrected query must be directly justified by the ORIGINAL USER QUESTION.

PREVIOUS JOB / EMPLOYMENT HISTORY RULES:
26. When the question asks for previous jobs, past jobs, or employment history, use job_history to identify historical job records.
27. job_history.JOB_ID identifies the historical job.
28. jobs.JOB_ID is the referenced job identifier.
29. jobs.job_title contains the human-readable job title.
30. When previous job titles are requested, connect:
    job_history.JOB_ID = jobs.JOB_ID
31. When previous job titles are requested, SELECT jobs.job_title rather than job_history.JOB_ID.
32. If employee names are explicitly requested along with previous jobs, connect:
    job_history.EMPLOYEE_ID = employees.EMPLOYEE_ID
33. If the question only says "previous jobs of employees" and does NOT explicitly request employee names or employee attributes, do NOT automatically join employees.
34. Do NOT add departments, locations, countries, or regions to a previous-jobs query unless explicitly requested.
35. Do NOT add a WHERE condition to a previous-jobs query unless the user explicitly asks for filtering.

FINAL CHECK BEFORE OUTPUT:
Before returning the corrected SQL, verify all of the following:
- Every table exists in the relevant schema.
- Every column exists in the relevant schema.
- Every JOIN condition exists in VALID JOIN RELATIONSHIPS.
- No relationship is incorrectly used as a WHERE condition.
- No unnecessary table is included.
- No unnecessary WHERE condition is included.
- No invented value is present.
- No column is referenced using the wrong table alias.
- The query directly answers the ORIGINAL USER QUESTION.
- The query is a single MySQL SELECT query.

OUTPUT RULES:
36. Return ONLY one valid MySQL SELECT query.
37. Do NOT use markdown.
38. Do NOT explain the query.
39. Do NOT include ```sql or ```.
40. Do NOT generate multiple queries.

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