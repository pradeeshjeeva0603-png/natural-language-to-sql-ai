import mysql.connector
def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pradeesh@0076",
        database="quantumedge_corporation"
    )
    return connection
