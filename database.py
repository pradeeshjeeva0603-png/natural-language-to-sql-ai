import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connection_timeout=10,
    )

    cursor = connection.cursor()
    cursor.execute("SET SESSION TRANSACTION READ ONLY")
    cursor.execute("SET SESSION MAX_EXECUTION_TIME=5000")  # kill SELECTs after 5s
    cursor.close()

    return connection
