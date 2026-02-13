
import streamlit as st
import re
from database import create_connection, create_table
from auth import hash_password, check_password, generate_token

create_table()

# ---------------- SESSION ----------------

if "page" not in st.session_state:
    st.session_state.page = "login"

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- AUTH PAGE STYLING ----------------

if st.session_state.page in ["login", "signup", "forgot"]:
    st.markdown("""
    <style>
    .stApp { background: #f3f4f6; }
    .block-container {
        max-width: 450px;
        margin: 80px auto;
        padding: 35px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    }
    .stButton > button {
        width: 100%;
        height: 42px;
        border-radius: 8px;
        background-color: #4F46E5;
        color: white;
        font-weight: 600;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN ----------------

def login_page():
    st.title("PolicyNav")
    st.subheader("Welcome Back")

    email = st.text_input("Email").strip()
    password = st.text_input("Password", type="password").strip()

    if st.button("Login"):

        if not email or not password:
            st.error("All fields required")
            return

        if not re.match(r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$", email):
            st.error("Invalid email format")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password(password, user[1]):
            generate_token(email)
            st.session_state.username = user[0]
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Forgot"):
            st.session_state.page = "forgot"
            st.rerun()
    with col2:
        if st.button("Signup"):
            st.session_state.page = "signup"
            st.rerun()

# ---------------- SIGNUP ----------------

def signup_page():
    st.title("PolicyNav")
    st.subheader("Create Account")

    username = st.text_input("Username").strip()
    email = st.text_input("Email").strip()
    password = st.text_input("Password", type="password").strip()
    confirm = st.text_input("Confirm Password", type="password").strip()
    question = st.selectbox("Security Question", [
        "Pet name?",
        "Mother's maiden name?",
        "Favorite teacher?"
    ])
    answer = st.text_input("Security Answer").strip()

    if st.button("Create Account"):

        if not all([username, email, password, confirm, answer]):
            st.error("All fields required")
            return

        if len(username) < 3:
            st.error("Username must be at least 3 characters")
            return

        if not re.match(r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$", email):
            st.error("Invalid email format")
            return

        if len(password) < 8 or \
           not re.search(r"[A-Z]", password) or \
           not re.search(r"[a-z]", password) or \
           not re.search(r"\d", password):
            st.error("Password must be 8+ chars with upper, lower and number")
            return

        if password != confirm:
            st.error("Passwords do not match")
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO users (username, email, password, security_question, security_answer)
            VALUES (?, ?, ?, ?, ?)
            """, (username, email, hash_password(password), question, answer))
            conn.commit()
            st.success("Account created!")
            st.session_state.page = "login"
            st.rerun()
        except:
            st.error("Email already exists")
        conn.close()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- FORGOT PASSWORD ----------------

def forgot_password_page():
    st.title("PolicyNav")
    st.subheader("Reset Password")

    if "step" not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        email = st.text_input("Registered Email").strip()

        if st.button("Verify Email"):
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT security_question, security_answer FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()

            if user:
                st.session_state.reset_email = email
                st.session_state.correct_answer = user[1]
                st.session_state.question = user[0]
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Email not found")

    elif st.session_state.step == 2:
        st.info(st.session_state.question)
        answer = st.text_input("Answer").strip()

        if st.button("Verify Answer"):
            if answer == st.session_state.correct_answer:
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("Wrong answer")

    elif st.session_state.step == 3:
        new_pass = st.text_input("New Password", type="password").strip()
        confirm = st.text_input("Confirm Password", type="password").strip()

        if st.button("Update Password"):
            if new_pass != confirm:
                st.error("Passwords do not match")
                return

            if len(new_pass) < 8:
                st.error("Password must be at least 8 characters")
                return

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE email = ?",
                           (hash_password(new_pass), st.session_state.reset_email))
            conn.commit()
            conn.close()

            st.success("Password updated")
            st.session_state.step = 1
            st.session_state.page = "login"
            st.rerun()

    if st.button("Back"):
        st.session_state.page = "login"
        st.session_state.step = 1
        st.rerun()

# ---------------- DASHBOARD ----------------

def dashboard():
    st.title("PolicyNav Dashboard")
    st.success(f"Welcome {st.session_state.username}")

    st.write("You are logged in successfully.")

    if st.button("Logout"):
        st.session_state.page = "login"
        st.session_state.username = ""
        st.rerun()

# ---------------- ROUTING ----------------

if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "forgot":
    forgot_password_page()
elif st.session_state.page == "dashboard":
    dashboard()
