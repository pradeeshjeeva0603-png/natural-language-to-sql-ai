from sentence_transformers import SentenceTransformer
from schema import SCHEMA_DOCUMENTS

TABLE_RELATIONSHIPS = {
    "employees": ["jobs", "departments"],
    "departments": ["employees", "locations"],
    "jobs": ["employees", "job_history"],
    "locations": ["departments", "countries"],
    "countries": ["locations", "regions"],
    "regions": ["countries"],
    "job_history": ["employees", "jobs", "departments"],
}

# Load a local embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Create embeddings for every schema document
table_names = list(SCHEMA_DOCUMENTS.keys())
schema_documents = list(SCHEMA_DOCUMENTS.values())

schema_embeddings = model.encode(schema_documents)

def expand_related_tables(table_names):
    expanded_tables = set(table_names)

    # Employees + Locations need Departments as the bridge
    if "employees" in table_names and "locations" in table_names:
        expanded_tables.add("departments")

    # Departments + Countries need Locations as the bridge
    if "departments" in table_names and "countries" in table_names:
        expanded_tables.add("locations")

    # Countries + Regions already have a direct relationship
    if "countries" in table_names and "regions" in table_names:
        expanded_tables.add("regions")

    # Job history needs Employees and Departments for related information
    if "job_history" in table_names:
        expanded_tables.add("employees")
        expanded_tables.add("departments")

    return expanded_tables

def get_keyword_tables(question):
    question = question.lower()
    tables = set()

    if any(word in question for word in [
        "employee", "employees", "salary", "salaries",
        "hire", "hired", "manager"
    ]):
        tables.add("employees")

    if any(word in question for word in [
        "department", "departments"
    ]):
        tables.add("departments")

    if any(word in question for word in [
        "job", "jobs", "job title", "position"
    ]):
        tables.add("jobs")

    if any(word in question for word in [
        "location", "city", "cities", "state", "address"
    ]):
        tables.add("locations")

    if any(word in question for word in [
        "country", "countries"
    ]):
        tables.add("countries")

    if any(word in question for word in [
        "region", "regions"
    ]):
        tables.add("regions")

    if any(word in question for word in [
        "history", "previous job", "past job"
    ]):
        tables.add("job_history")

    return tables


def retrieve_schema(question, top_k=3):
    # 1. Keyword-based table detection
    keyword_tables = get_keyword_tables(question)

    # 2. Vector similarity search
    question_embedding = model.encode([question])[0]

    similarities = model.similarity(
        question_embedding.reshape(1, -1),
        schema_embeddings
    )[0]

    top_indices = similarities.argsort(descending=True)[:top_k]

    vector_tables = set()

    for index in top_indices:
        vector_tables.add(table_names[index])

    # 3. Combine keyword + vector results
    if keyword_tables:
        initial_tables = keyword_tables
    else:
        initial_tables = vector_tables

    # 4. Expand using foreign-key relationships
    relevant_tables = expand_related_tables(initial_tables)

    # 5. Return the corresponding schema documents
    retrieved_documents = []

    for table in table_names:
        if table in relevant_tables:
            retrieved_documents.append(SCHEMA_DOCUMENTS[table])

    return "\n".join(retrieved_documents), relevant_tables

if __name__ == "__main__":
    question = input("Enter a database question: ")

    print("\nRetrieved Schema:")
    print(retrieve_schema(question))

