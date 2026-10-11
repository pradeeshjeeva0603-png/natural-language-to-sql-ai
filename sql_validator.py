import re
import sqlglot
from sqlglot import exp

# Tables the LLM may query. Load this from your schema in practice.
ALLOWED_TABLES = {"employees", "departments", "jobs", "locations",
                  "countries", "regions", "job_history"}

BLOCKED_FUNCTIONS = {"SLEEP", "BENCHMARK", "LOAD_FILE", "GET_LOCK",
                     "RELEASE_LOCK", "SYS_EXEC", "SYS_EVAL"}

MAX_JOINED_TABLES = 5


def clean_llm_sql(raw: str) -> str:
    """Strip markdown fences / stray text the model may add."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:sql)?\s*", "", raw, flags=re.I)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def validate_sql(sql: str, allowed_tables=ALLOWED_TABLES):
    sql = clean_llm_sql(sql)
    if not sql:
        return False, "SQL query is empty."

    try:
        statements = [s for s in sqlglot.parse(sql, read="mysql") if s]
    except sqlglot.errors.ParseError as e:
        return False, f"Could not parse SQL: {str(e)[:120]}"

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    tree = statements[0]

    if not isinstance(tree, (exp.Select, exp.Union)):
        return False, "Only SELECT queries are allowed."

    # Any write / DDL / file-output node anywhere in the tree
    banned_nodes = (exp.Insert, exp.Update, exp.Delete, exp.Drop,
                    exp.Create, exp.Alter, exp.Command, exp.Into,
                    exp.Lock)
    for node in tree.walk():
        n = node[0] if isinstance(node, tuple) else node
        if isinstance(n, banned_nodes):
            return False, f"Forbidden operation: {type(n).__name__}"
        if isinstance(n, exp.Anonymous) and n.name.upper() in BLOCKED_FUNCTIONS:
            return False, f"Forbidden function: {n.name}"
        if isinstance(n, exp.Func) and type(n).__name__.upper() in BLOCKED_FUNCTIONS:
            return False, f"Forbidden function: {type(n).__name__}"

    # Table allowlist (CTE names are fine)
    cte_names = {c.alias_or_name.lower() for c in tree.find_all(exp.CTE)}
    tables = list(tree.find_all(exp.Table))
    for t in tables:
        if t.db:
            return False, "Cross-database queries are not allowed."
        name = t.name.lower()
        if name not in allowed_tables and name not in cte_names:
            return False, f"Table not allowed: {t.name}"

    if len(tables) > MAX_JOINED_TABLES:
        return False, "Query touches too many tables."

    return True, "SQL is valid."


def enforce_limit(sql: str, max_rows: int = 500) -> str:
    """Add LIMIT if missing; cap it if too large."""
    tree = sqlglot.parse_one(clean_llm_sql(sql), read="mysql")
    limit = tree.args.get("limit")
    if limit is None:
        tree = tree.limit(max_rows)
    else:
        try:
            if int(limit.expression.name) > max_rows:
                tree = tree.limit(max_rows)
        except (ValueError, AttributeError):
            pass
    return tree.sql(dialect="mysql")
