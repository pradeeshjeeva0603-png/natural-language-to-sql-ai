from schema import SCHEMA_DOCUMENTS


def retrieve_schema(question):
    question = question.lower()

    relevant_tables = set()

    # Employees
    if any(word in question for word in [
        "employee", "employees", "salary", "salaries",
        "hire", "hired", "manager"
    ]):
        relevant_tables.add("employees")

    # Departments
    if any(word in question for word in [
        "department", "departments"
    ]):
        relevant_tables.add("departments")

    # Jobs
    if any(word in question for word in [
        "job", "jobs", "job title", "position"
    ]):
        relevant_tables.add("jobs")

    # Locations
    if any(word in question for word in [
        "location", "city", "state", "address"
    ]):
        relevant_tables.add("locations")

    # Countries
    if any(word in question for word in [
        "country", "countries"
    ]):
        relevant_tables.add("countries")

    # Regions
    if any(word in question for word in [
        "region", "regions"
    ]):
        relevant_tables.add("regions")

    # Job history
    if any(word in question for word in [
        "history", "previous job", "past job"
    ]):
        relevant_tables.add("job_history")

    # If nothing relevant was detected,
    # provide the complete schema.
    if not relevant_tables:
        return "\n".join(SCHEMA_DOCUMENTS.values())

    # Return only relevant schema documents
    retrieved_schema = []

    for table in relevant_tables:
        retrieved_schema.append(SCHEMA_DOCUMENTS[table])

    return "\n".join(retrieved_schema)

