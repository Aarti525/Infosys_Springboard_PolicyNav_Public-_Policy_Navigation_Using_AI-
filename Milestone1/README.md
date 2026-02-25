# 🔐 User Authentication Module (Milestone 1)

## 📌 Project Overview
This module implements a **secure user authentication system** using **Streamlit** and **SQLite**.  
It provides **Signup**, **Login**, and **Forgot Password** functionality using **security questions**.

This module is developed as part of **Milestone 1** and focuses only on **user authentication**.

---

## 🎯 Features Implemented

### ✅ 1. User Signup
- New users can create an account
- Fields included:
  - Username
  - Email (unique)
  - Password
  - Confirm Password
  - Security Question
  - Security Answer
- Validations:
  - All fields required
  - Password and confirm password must match
  - Email must be unique

---

### ✅ 2. User Login
- Registered users can log in using:
  - Email
  - Password
- Validations:
  - Incorrect email or password is handled properly
- On successful login:
  - User is redirected to a **Dashboard**
  - Displays a **Welcome message with user email**

---

### ✅ 3. Forgot Password (Security Question Based)
- User can reset password using:
  - Registered email
  - Security question & answer
- Validations:
  - Email must exist
  - Security answer must match
  - New password confirmation required
- Password is updated securely in the database

---

## 🧰 Technologies Used

- **Frontend:** Streamlit  
- **Backend:** Python  
- **Database:** SQLite (`users.db`)  
- **Security:**  
  - Password hashing  
  - Security question verification  


## ⚙ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Aarti525/Infosys_Springboard_PolicyNav_Public-_Policy_Navigation_Using_AI-.git
cd milestone1
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install streamlit bcrypt textstat plotly PyPDF2 python-docx
```

### 4️⃣ Run Application

```bash
streamlit run app.py
.\ngrok http 8501
```
---

## 🗄 Database Information

- SQLite database (`users.db`) auto-generates on first run
- Stores user credentials securely
- Passwords are hashed using bcrypt
- Includes role-ready structure (admin flag supported)

---


## 👨‍💻 Developed For

Milestone 1 Academic Submission  
Infosys LLM – Readability Dashboard


## Screenshots
### Signup Page
![Signup Page](screenshots/signup.png)

### Login Page
![Login Page](screenshots/login.png)

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Forgot Password
![Forgot Password](screenshots/forgotpassword.png)

