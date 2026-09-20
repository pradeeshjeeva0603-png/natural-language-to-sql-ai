from database import get_connection
from schema import DATABASE_SCHEMA


def main():
    print("======================================")
    print("   AI DATABASE ASSISTANT")
    print("======================================")

    print("\nDatabase schema loaded successfully.")
    print(DATABASE_SCHEMA[:500] + "...")

    question = input("\nAsk a question about the database: ")

    print("\nYour question:")
    print(question)


if __name__ == "__main__":
    main()
