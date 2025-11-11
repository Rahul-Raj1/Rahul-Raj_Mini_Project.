import streamlit as st
import mysql.connector
from datetime import datetime
import hashlib

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
    host="aws.connect.psdb.cloud",
    user="8qyzpxxxxx",
    password="pscale_xxxxxx",
    database="client_query_system",
    ssl_ca="cacert.pem"
    )
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None


# ---------- HELPER FUNCTIONS ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        # Users table (for login)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255),
                role ENUM('Client','Support')
            )
        """)
        # Queries table (same as before)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS client_queries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_id INT,
                client_name VARCHAR(100),
                email VARCHAR(100),
                mobile VARCHAR(20),
                heading VARCHAR(255),
                description TEXT,
                status VARCHAR(20) DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at DATETIME NULL,
                FOREIGN KEY (client_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        cur.close()
        conn.close()

create_tables()


# ---------- PAGE TITLE ----------
st.set_page_config(page_title="Client Query System", layout="centered")
st.title("Client Query Management System")


# ---------- LOGIN / REGISTER ----------
menu = st.sidebar.radio("Menu", ["Login", "Register"])
role = st.sidebar.selectbox("Select Role", ["Client", "Support"])

# --- REGISTER SECTION ---
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
                cur.execute("INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                            (name, email, hash_password(password), role))
                conn.commit()
                st.success(f"✅ Registered successfully as {role}. Please login now.")
            except mysql.connector.errors.IntegrityError:
                st.error("❌ Email already exists. Try another one.")
            finally:
                cur.close()
                conn.close()

# --- LOGIN SECTION ---
elif menu == "Login":
    st.subheader(f"🔐 Login as {role}")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s AND password_hash=%s AND role=%s",
                    (email, hash_password(password), role))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            st.session_state["user"] = user
            st.success(f"✅ Welcome {user['name']}! Logged in as {user['role']}.")
        else:
            st.error("❌ Invalid credentials or role mismatch.")


# ---------- MAIN APP AFTER LOGIN ----------
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
                try:
                    cur.execute("""
                        INSERT INTO client_queries (client_id, client_name, email, mobile, heading, description, status, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, 'Open', %s)
                    """, (user["id"], user["name"], user["email"], mobile, heading, description, datetime.now()))
                    conn.commit()
                    st.success("✅ Your query has been submitted successfully and saved in MySQL.")
                except Exception as e:
                    st.error(f"❌ Failed to save query: {e}")
                finally:
                    cur.close()
                    conn.close()

    # ---------- SUPPORT SECTION ----------
    # ---------- SUPPORT SECTION ----------
elif role == "Support":
    st.subheader("📋 Support Team Dashboard")

    conn = get_db_connection()

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            # ✅ Fetch all client queries
            cursor.execute("""
                SELECT 
                    id,
                    client_name,
                    email,
                    mobile,
                    heading,
                    description,
                    status,
                    created_at,
                    closed_at
                FROM client_queries
                ORDER BY created_at DESC
            """)
            queries = cursor.fetchall()

            if len(queries) == 0:
                st.info("No client queries found yet.")
            else:
                st.write("### ✅ All Client Queries")

                # ✅ Show query table
                st.dataframe(queries, use_container_width=True)

                st.write("---")
                st.write("### 🔧 Manage Queries")

                # ✅ Display each record with a Close button
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

                        # ✅ Show Close Button Only If Query Is Open
                        if q["status"] == "Open":
                            if st.button(f"Close Query #{q['id']}"):
                                cursor2 = conn.cursor()
                                cursor2.execute("""
                                    UPDATE client_queries
                                    SET status='Closed', closed_at=%s
                                    WHERE id=%s
                                """, (datetime.now(), q["id"]))
                                conn.commit()
                                st.success(f"✅ Query #{q['id']} is now Closed.")
                                st.rerun()
                        else:
                            st.info(f"✅ Closed At: {q['closed_at']}")

        except Exception as e:
            st.error(f"❌ Error fetching queries: {e}")
        finally:
            cursor.close()
            conn.close()

