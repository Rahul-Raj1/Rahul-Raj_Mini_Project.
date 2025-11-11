import sqlite3
import streamlit as st
from datetime import datetime

# ------------------------------
# DATABASE FUNCTIONS
# ------------------------------

def get_connection():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS client_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            title TEXT,
            message TEXT,
            status TEXT DEFAULT 'Open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            closed_at TEXT,
            FOREIGN KEY(client_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    
def register_user(username, password, role):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                    (username, password, role))
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    return user

def submit_query(client_id, title, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO client_queries (client_id, title, message)
        VALUES (?, ?, ?)
    """, (client_id, title, message))
    conn.commit()
def fetch_all_queries():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT client_queries.*, users.username 
        FROM client_queries 
        JOIN users ON client_queries.client_id = users.id
        ORDER BY created_at DESC
    """)
    return cur.fetchall()
def close_query(query_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE client_queries
        SET status='Closed', closed_at=?
        WHERE id=?
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), query_id))
    conn.commit()
st.title("Client Query Management System (SQLite Version)")

create_tables()

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Create New Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Client", "Support"])
    if st.button("Register"):
        if register_user(username, password, role):
            st.success("Registration successful!")
        else:
            st.error("Username already exists!")

elif choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(username, password)
        if user:
            st.success(f"Welcome {user['username']} ({user['role']})")

            # CLIENT PANEL
            if user["role"] == "Client":
                st.subheader("Submit a Query")
                title = st.text_input("Query Title")
                message = st.text_area("Query Description")

                if st.button("Submit Query"):
                    submit_query(user["id"], title, message)
                    st.success("Query submitted!")

            # SUPPORT PANEL
            elif user["role"] == "Support":
                st.subheader("All Client Queries")
                data = fetch_all_queries()

                for row in data:
                    st.write(f"### {row['title']}")
                    st.write(f"Client: {row['username']}")
                    st.write(f"Message: {row['message']}")
                    st.write(f"Status: {row['status']}")
                    st.write(f"Created at: {row['created_at']}")
                    st.write("---")

                    if row["status"] == "Open":
                        if st.button(f"Close Query {row['id']}"):
                            close_query(row["id"])
                            st.success("Query closed!")
                            st.experimental_rerun()
        else:
            st.error("Invalid username or password")



