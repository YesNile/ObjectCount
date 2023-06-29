import psycopg2
from config import host, user, password, database, port

con = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=port
)
print("Database opened successfully")
