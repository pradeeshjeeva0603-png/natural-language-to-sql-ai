import sqlparse


FORBIDDEN_KEYWORDS = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "RENAME",
}


def validate_sql(sql):
    sql = sql.strip()

    if not sql:
        return False, "SQL query is empty."

    statements = sqlparse.parse(sql)

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    statement = statements[0]

    # Only SELECT statements are allowed
    if statement.get_type() != "SELECT":
        return False, "Only SELECT queries are allowed."

    # Check SQL tokens for forbidden operations
    sql_upper = sql.upper()

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in sql_upper:
            return False, f"Forbidden SQL operation detected: {keyword}"

    return True, "SQL is valid."