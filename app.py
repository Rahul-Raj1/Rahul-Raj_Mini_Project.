import streamlit as st
import sqlite3
from datetime import datetime
import hashlib
import os

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    conn = sqlite3.connect("client_query_system.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------- INITIALIZE DATABASE ----------
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # Users table (for login)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password_hash TEXT,
            role TEXT CHECK(role IN ('Client','Support'))
        )
    """)

    # Queries table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS client_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            client_name TEXT,
            email TEXT,
            mobile TEXT,
            heading TEXT,
            description TEXT,
            status TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# Create tables if not exist
create_tables()


# ---------- HELPER FUNCTIONS ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Client Query System", layout="centered")
st.title("Client Query Management System")


# ---------- SIDEBAR ----------
menu = st.sidebar.radio("Menu", ["Login", "Register"])
role = st.sidebar.selectbox("Select Role", ["Client", "Support"])


# ---------- REGISTER ----------
if menu == "Register":
    st.subheader(f"📝 Register as {role}")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if not (name and email and password):
            st.warning("⚠ Please fill all fields")
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                            (name, email, hash_password(password), role))
                conn.commit()
                st.success(f"✅ Registered successfully as {role}. Please login now.")
            except sqlite3.IntegrityError:
                st.error("❌ Email already exists. Try another one.")
            finally:
                cur.close()
                conn.close()


# ---------- LOGIN ----------
elif menu == "Login":
    st.subheader(f"🔐 Login as {role}")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password_hash=? AND role=?",
                    (email, hash_password(password), role))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            st.session_state["user"] = dict(user)
            st.success(f"✅ Welcome {user['name']}! Logged in as {user['role']}.")
        else:
            st.error("❌ Invalid credentials or role mismatch.")


# ---------- MAIN APP ----------
if "user" in st.session_state:
    user = st.session_state["user"]

    # ---------- CLIENT SECTION ----------
    if user["role"] == "Client":
        st.subheader("🧾 Submit Your Query")

        with st.form("client_query_form"):
            mobile = st.text_input("📱 Mobile Number")
            heading = st.text_input("📝 Query Heading")
            description = st.text_area("💬 Describe your issue here...")
            submit_query = st.form_submit_button("Submit Query")

        if submit_query:
            if not (heading and description):
                st.warning("⚠ Please fill all required fields before submitting.")
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO client_queries (client_id, client_name, email, mobile, heading, description, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'Open', ?)
                """, (user["id"], user["name"], user["email"], mobile, heading, description, datetime.now()))
                conn.commit()
                cur.close()
                conn.close()
                st.success("✅ Your query has been submitted successfully.")

    # ---------- SUPPORT SECTION ----------
    elif user["role"] == "Support":
        st.subheader("📋 Support Team Dashboard")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, client_name, email, mobile, heading, description, status, created_at, closed_at
            FROM client_queries
            ORDER BY created_at DESC
        """)
        queries = cur.fetchall()

        if len(queries) == 0:
            st.info("No client queries found yet.")
        else:
            st.write("### ✅ All Client Queries")
            st.dataframe(queries, use_container_width=True)

            st.write("---")
            st.write("### 🔧 Manage Queries")

            for q in queries:
                with st.expander(f"🆔 Query #{q['id']} — {q['heading']}"):
                    st.markdown(f"""
                    **👤 Client:** {q['client_name']}  
                    **📧 Email:** {q['email']}  
                    **📱 Mobile:** {q['mobile']}  
                    **📝 Description:** {q['description']}  
                    **📅 Created:** {q['created_at']}  
                    **📌 Status:** {q['status']}  
                    """)

                    if q["status"] == "Open":
                        if st.button(f"Close Query #{q['id']}"):
                            cur2 = conn.cursor()
                            cur2.execute("""
                                UPDATE client_queries
                                SET status='Closed', closed_at=?
                                WHERE id=?
                            """, (datetime.now(), q["id"]))
                            conn.commit()
                            cur2.close()
                            st.success(f"✅ Query #{q['id']} closed.")
                            st.rerun()
                    else:
                        st.info(f"✅ Closed At: {q['closed_at']}")

        cur.close()
        conn.close()
