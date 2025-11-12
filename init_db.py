import sqlite3

# Create a database file
conn = sqlite3.connect("client_query_system.db")
cur = conn.cursor()

# Run the SQL commands from database.sql
with open("database.sql", "r") as f:
    sql_script = f.read()

cur.executescript(sql_script)

conn.commit()
conn.close()

print("✅ Database and tables created successfully!")
