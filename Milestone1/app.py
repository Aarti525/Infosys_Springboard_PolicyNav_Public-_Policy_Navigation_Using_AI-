
import streamlit as st
import time
import re
import bcrypt
import database as db

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Secure App", page_icon="🔐", layout="centered")

# ---------------- LIGHT COLORFUL UI ----------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f7fa;
    color: #0f172a;
}
h1, h2, h3 {
    color: #0f172a;
}
.stTextInput input {
    background-color: white;
    border-radius: 6px;
}
.stButton button {
    background-color: #6366f1;
    color: white;
    border-radius: 6px;
    width: 100%;
}
.stButton button:hover {
    background-color: #4f46e5;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- HELPERS ----------------
def switch_page(page):
    st.session_state.page = page
    st.rerun()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.error("All fields are required")
        elif db.authenticate_user(email, password):
            st.session_state.user = email
            switch_page("dashboard")
        else:
            st.error("Invalid email or password")

    st.markdown("---")
    if st.button("Create Account"):
        switch_page("signup")

    if st.button("Forgot Password"):
        switch_page("forgot")

# ---------------- SIGNUP PAGE ----------------
def signup_page():
    st.title("📝 Sign Up")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    question = st.selectbox(
        "Security Question",
        [
            "What is your favorite color?",
            "What is your pet's name?",
            "What is your birth city?"
        ]
    )

    answer = st.text_input("Security Answer")

    if st.button("Create Account"):
        if not username or not email or not password or not answer:
            st.error("All fields are required")
        elif password != confirm:
            st.error("Passwords do not match")
        else:
            success = db.register_user(
                username,
                email,
                password,
                question,
                answer
            )

            if success:
                st.success("Account created successfully")
                st.session_state["page"] = "login"
            else:
                st.error("Email already exists")

    if st.button("⬅ Back to Login"):
        st.session_state["page"] = "login"

# ---------------- FORGOT PASSWORD ----------------
def forgot_page():
    st.title("🔑 Forgot Password")

    email = st.text_input("Registered Email")

    if st.button("Next"):
        if not email:
            st.error("Email required")
        elif not db.check_user_exists(email):
            st.error("User not found")
        else:
            st.session_state.reset_email = email
            st.session_state.page = "security_check"
            st.rerun()

    if st.button("⬅ Back to Login"):
        switch_page("login")

# ---------------- SECURITY QUESTION PAGE ----------------
def security_check_page():
    st.title("🛡 Security Verification")

    email = st.session_state.reset_email
    question, stored_hash = db.get_security_question(email)

    if not question:
        st.error("Security question not found")
        return

    st.info(question)
    answer = st.text_input("Your Answer", type="password")

    if st.button("Verify"):
        if bcrypt.checkpw(answer.encode(), stored_hash):
            switch_page("reset_password")
        else:
            st.error("Incorrect answer")

# ---------------- RESET PASSWORD ----------------
def reset_password_page():
    st.title("🔁 Reset Password")

    new_pass = st.text_input("New Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Update Password"):
        if not new_pass or not confirm:
            st.error("All fields required")
        elif new_pass != confirm:
            st.error("Passwords do not match")
        else:
            db.update_password(st.session_state.reset_email, new_pass)
            st.success("Password updated successfully")
            time.sleep(1)
            switch_page("login")

# ---------------- DASHBOARD ----------------
def dashboard_page():
    st.title("🎉 Welcome Back")
    st.success(f"Logged in as: {st.session_state.user}")

    if st.button("Log Out"):
        st.session_state.user = None
        switch_page("login")

# ---------------- ROUTING ----------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "forgot":
    forgot_page()
elif st.session_state.page == "security_check":
    security_check_page()
elif st.session_state.page == "reset_password":
    reset_password_page()
elif st.session_state.page == "dashboard":
    dashboard_page()



