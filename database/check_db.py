import sqlite3

DATABASE = 'database/petadoption.db'

try:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    if tables:
        print("Tables in the database:", tables)
    else:
        print("No tables found. The database might not be initialized.")
    conn.close()
except sqlite3.DatabaseError as e:
    print("Error:", e)

