# Open POS API

A modern Point-of-Sale (POS) backend and management REST API built with **Flask**, **PostgreSQL**, and **Flask-Admin**.

---

## 🚀 Quick Start

### 1. Create & Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install "setuptools<70"
pip install -r requirements.txt
```

### 3. Configure Database
Ensure PostgreSQL is running, create the database in pgAdmin or psql:
```sql
CREATE DATABASE "pos";
```
Ensure [.env](.env) contains your database connection string:
```env
POSTGRE_CONNECTION_STRING=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/pos
```

### 4. Initialize Database & Create Admin User
```powershell
# Create database tables
flask create-db

# Create initial admin account
flask create-admin -e admin@pos.com -p "admin123" -n "Admin User" -m "9999999999"
```

### 5. Run the Server
```powershell
flask run
```
The server will start at: `http://127.0.0.1:5000/`

---

## 🔑 Access Points

- **Admin Dashboard:** [http://127.0.0.1:5000/admin/](http://127.0.0.1:5000/admin/)
- **API Login Endpoint:** [http://127.0.0.1:5000/api/v1/login/](http://127.0.0.1:5000/api/v1/login/)
- **Default Admin Credentials:**
  - **Email:** `admin@pos.com`
  - **Password:** `admin123`

---

## 📚 Documentation

Detailed documentation available in this repository:

- 📖 **[Setup & Troubleshooting Guide](SETUP.md)** — Step-by-step installation, prerequisites, and common fixes.
- 🔌 **[API Reference](API_REFERENCE.md)** — Complete list of REST API endpoints and payload examples.
- 🏗️ **[System Architecture](ARCHITECTURE.md)** — Project structure, database models, and design patterns.
