FORBIDDEN_KEYWORDS = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "RENAME",
]


def validate_sql(sql):
    sql_upper = sql.strip().upper()

    # Only allow SELECT queries
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed."

    # Check for dangerous SQL operations
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in sql_upper:
            return False, f"Forbidden SQL operation detected: {keyword}"

    return True, "SQL is valid."

