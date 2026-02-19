import streamlit as st
import sqlite3
import bcrypt
import re
import textstat
import plotly.graph_objects as go
import random
import datetime
import smtplib
from email.mime.text import MIMEText
from PyPDF2 import PdfReader
from docx import Document

# ================= CONFIG =================

st.set_page_config(page_title="PolicyNav Intelligence", layout="wide")

EMAIL_ADDRESS = "aartichandolkar7@gmail.com"
EMAIL_PASSWORD = "evvheiylhjvmmoje"

# ================= CUSTOM UI =================

st.markdown("""
<style>
body {background-color:#f5f7fb;}
.stButton>button {
    background: linear-gradient(90deg,#4f46e5,#06b6d4);
    color:white;
    border-radius:8px;
    padding:8px 18px;
}
h1,h2,h3 {color:#1e293b;}
</style>
""", unsafe_allow_html=True)

# ================= DATABASE =================

def create_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password BLOB,
            security_question TEXT,
            security_answer TEXT,
            is_admin INTEGER DEFAULT 0,
            otp_attempts INTEGER DEFAULT 0
        )
    """)
    return conn

# ================= VALIDATIONS =================

def validate_email(email):
    return re.match(r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$", email)

def validate_password(password):
    if len(password) < 8: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[0-9]", password): return False
    return True

def password_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[0-9]", password): score += 1
    if re.search(r"[!@#$%^&*]", password): score += 1
    return score

# ================= SECURITY =================

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# ================= EMAIL OTP =================

def send_otp_email(receiver_email, otp):
    try:
        msg = MIMEText(f"Your OTP is {otp}. Valid for 5 minutes.")
        msg["Subject"] = "PolicyNav OTP"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = receiver_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver_email, msg.as_string())
        server.quit()
        return True
    except:
        return False

# ================= FILE READING =================

def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")

    elif file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    elif "word" in file.type:
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    return ""

# ================= READABILITY =================

def compute_metrics(text):
    return {
        "FRE": textstat.flesch_reading_ease(text),
        "FKGL": textstat.flesch_kincaid_grade(text),
        "GunningFog": textstat.gunning_fog(text),
        "SMOG": textstat.smog_index(text),
        "ColemanLiau": textstat.coleman_liau_index(text),
        "Sentences": textstat.sentence_count(text),
        "Words": textstat.lexicon_count(text),
        "Characters": textstat.char_count(text)
    }

def interpret_readability(metrics):

    fre = metrics["FRE"]
    fkgl = metrics["FKGL"]

    if fre >= 90:
        level = "Very Easy"
        color = "green"
    elif fre >= 80:
        level = "Easy"
        color = "green"
    elif fre >= 70:
        level = "Fairly Easy"
        color = "blue"
    elif fre >= 60:
        level = "Standard"
        color = "orange"
    elif fre >= 50:
        level = "Fairly Difficult"
        color = "orange"
    elif fre >= 30:
        level = "Difficult"
        color = "red"
    else:
        level = "Very Difficult / Expert"
        color = "red"

    return level, color, round(fkgl, 1)


def gauge_chart(title, value, min_val, max_val, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(value,2),
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': color}
        }
    ))
    fig.update_layout(height=260)
    return fig

# ================= SESSION =================

if "page" not in st.session_state:
    st.session_state.page = "login"

# ================= SIGNUP =================

def signup():
    st.title("Create Account")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if password:
        strength = password_strength(password)
        st.progress(strength / 4)
        st.caption("Password strength")

    security_question = st.selectbox("Security Question",
        ["What is your pet name?",
         "What is your favorite color?",
         "What is your birth city?"])

    security_answer = st.text_input("Security Answer")

    if st.button("Register"):
        if not username or not email or not password or not security_answer:
            st.error("All fields required")
            return

        if not validate_email(email):
            st.error("Invalid email")
            return

        if not validate_password(password):
            st.error("Weak password")
            return

        conn = create_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users(username,email,password,security_question,security_answer)
                VALUES(?,?,?,?,?)
            """,(username,email,hash_password(password),
                 security_question,security_answer.lower()))
            conn.commit()
            st.success("Registered successfully")
            st.session_state.page="login"
            st.rerun()
        except:
            st.error("Email already exists")

        conn.close()

    if st.button("Back"):
        st.session_state.page="login"
        st.rerun()

# ================= LOGIN =================

def login():
    st.title("PolicyNav Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not validate_email(email):
            st.error("Invalid email")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id,username,password,is_admin FROM users WHERE email=?",(email,))
        user=cursor.fetchone()
        conn.close()

        if user and check_password(password,user[2]):
            st.session_state.user_id=user[0]
            st.session_state.username=user[1]
            st.session_state.is_admin=user[3]
            st.session_state.page="dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Forgot Password"):
        st.session_state.page="forgot"
        st.rerun()

    if st.button("Signup"):
        st.session_state.page="signup"
        st.rerun()

# ================= FORGOT PASSWORD =================

def forgot_password():
    st.title("Reset Password")

    email = st.text_input("Registered Email")

    if st.button("Send OTP"):
        if not validate_email(email):
            st.error("Invalid email")
            return

        conn=create_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT id,security_question,otp_attempts FROM users WHERE email=?",(email,))
        user=cursor.fetchone()

        if user:
            otp=random.randint(100000,999999)
            if send_otp_email(email,otp):
                st.session_state.otp=str(otp)
                st.session_state.otp_expiry=datetime.datetime.now()+datetime.timedelta(minutes=5)
                st.session_state.reset_email=email
                st.session_state.security_question=user[1]
                st.success("OTP sent")
            else:
                st.error("Email sending failed")
        else:
            st.error("Email not found")
        conn.close()

    if "otp" in st.session_state:
        user_otp=st.text_input("Enter OTP")

        if st.button("Verify OTP"):
            if datetime.datetime.now()>st.session_state.otp_expiry:
                st.error("OTP expired")
                return

            if user_otp==st.session_state.otp:
                st.session_state.otp_verified=True
                st.success("OTP verified")
            else:
                st.error("Wrong OTP")

    if st.session_state.get("otp_verified"):
        st.info(st.session_state.security_question)
        answer=st.text_input("Security Answer")
        new_password=st.text_input("New Password",type="password")

        if new_password:
            st.progress(password_strength(new_password)/4)

        if st.button("Reset Password"):
            if not answer:
                st.error("Answer required")
                return
            if not validate_password(new_password):
                st.error("Weak password")
                return

            conn=create_connection()
            cursor=conn.cursor()
            cursor.execute("SELECT security_answer FROM users WHERE email=?",
                           (st.session_state.reset_email,))
            stored=cursor.fetchone()[0]

            if answer.lower()==stored:
                cursor.execute("UPDATE users SET password=? WHERE email=?",
                               (hash_password(new_password),
                                st.session_state.reset_email))
                conn.commit()
                st.success("Password reset successful")
                st.session_state.clear()
                st.session_state.page="login"
                st.rerun()
            else:
                st.error("Wrong security answer")
            conn.close()

    if st.button("Back"):
        st.session_state.clear()
        st.session_state.page="login"
        st.rerun()

# ================= DASHBOARD =================

def dashboard():

    st.sidebar.title("Infosys")
    st.sidebar.subheader("Infosys LLM")

    if st.session_state.is_admin:
        if st.sidebar.button("Admin Panel"):
            st.session_state.page="admin"
            st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.session_state.page="login"
        st.rerun()

    st.title("Readability Intelligence Dashboard")

    file=st.file_uploader("Upload TXT / PDF / DOCX",type=["txt","pdf","docx"])
    manual_text=st.text_area("Or paste text here")

    text=""

    if file:
        text=extract_text(file)
    elif manual_text:
        text=manual_text

    if st.button("Analyze"):
        if not text or len(text)<50:
            st.warning("Minimum 50 characters required")
            return

        metrics=compute_metrics(text)

        level, color, grade = interpret_readability(metrics)

        st.markdown("### 📘 Reading Level Summary")

        if color == "green":
          st.success(f"Reading Level: {level}")
        elif color == "blue":
          st.info(f"Reading Level: {level}")
        elif color == "orange":
          st.warning(f"Reading Level: {level}")
        else:
          st.error(f"Reading Level: {level}")

        st.write(f"📚 Estimated Education Level Required: Grade {grade}")


        c1,c2,c3=st.columns(3)
        c1.plotly_chart(gauge_chart("FRE",metrics["FRE"],0,100,"#4f46e5"),use_container_width=True)
        c2.plotly_chart(gauge_chart("FKGL",metrics["FKGL"],0,20,"#06b6d4"),use_container_width=True)
        c3.plotly_chart(gauge_chart("Gunning Fog",metrics["GunningFog"],0,20,"#f59e0b"),use_container_width=True)

        c4,c5=st.columns(2)
        c4.plotly_chart(gauge_chart("SMOG",metrics["SMOG"],0,20,"#ef4444"),use_container_width=True)
        c5.plotly_chart(gauge_chart("ColemanLiau",metrics["ColemanLiau"],0,20,"#10b981"),use_container_width=True)

        s1,s2,s3=st.columns(3)
        s1.metric("Sentences",metrics["Sentences"])
        s2.metric("Words",metrics["Words"])
        s3.metric("Characters",metrics["Characters"])

# ================= ADMIN PANEL =================

def admin_panel():
    st.title("Admin Panel")
    conn=create_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT username,email FROM users")
    users=cursor.fetchall()
    conn.close()

    for u in users:
        st.write(f"User: {u[0]} | Email: {u[1]}")

    if st.button("Back"):
        st.session_state.page="dashboard"
        st.rerun()

# ================= ROUTER =================

if st.session_state.page=="login":
    login()
elif st.session_state.page=="signup":
    signup()
elif st.session_state.page=="forgot":
    forgot_password()
elif st.session_state.page=="dashboard":
    dashboard()
elif st.session_state.page=="admin":
    admin_panel()






