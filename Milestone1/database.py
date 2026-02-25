import sqlite3
import bcrypt

DB_NAME = "users.db"


def create_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL,
        security_question TEXT NOT NULL,
        security_answer TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def register_user(username, email, password, question, answer):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        cursor.execute("""
        INSERT INTO users (username, email, password, security_question, security_answer)
        VALUES (?, ?, ?, ?, ?)
        """, (username, email, hashed_pw, question, answer))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def authenticate_user(email, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode(), user[0]):
        return True
    return False


def verify_security_answer(email, answer):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT security_answer FROM users WHERE email = ?", (email,)
    )
    data = cursor.fetchone()
    conn.close()

    if data and data[0].lower() == answer.lower():
        return True
    return False


def update_password(email, new_password):
    conn = create_connection()
    cursor = conn.cursor()

    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (hashed_pw, email)
    )

    conn.commit()
    conn.close()
