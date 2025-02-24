import sqlite3

# Define the path to your SQLite database file
DATABASE = 'petadoption.db'

# Define the path to your SQL file
SQL_FILE = 'init.sql'

def initialize_database():
    # Connect to the SQLite database (creates the file if it doesn't exist)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Open and read the SQL file
    with open(SQL_FILE, 'r') as f:
        sql_script = f.read()
    
    # Execute the SQL script (creates tables)
    try:
        cursor.executescript(sql_script)
    except sqlite3.DatabaseError as e:
        print(f"Database Error: {e}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    initialize_database()
