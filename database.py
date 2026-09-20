import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()
def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="quantumedge_corporation"
    )
    return connection