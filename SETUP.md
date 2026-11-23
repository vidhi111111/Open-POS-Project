# Open POS API - Setup Guide

This document explains how to set up, configure, and run the Open POS API project locally from scratch on a Windows machine with **Python 3.12** and **PostgreSQL**.

---

## 1. Prerequisites

Before starting, make sure you have:
- **Python 3.12** (or 3.11) installed (e.g., `C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe`)
- **PostgreSQL 16+ / 18** installed, running, and accessible via **pgAdmin 4** or `psql` (default port: `5432`)
- Windows PowerShell

---

## 2. Step-by-Step Installation

### Step 1: Navigate to the Project Directory
Open PowerShell and make sure you are in the directory containing `manager.py`:
```powershell
cd C:\Users\Admin\Downloads\open-pos-api-master-demo\open-pos-api-master\open-pos-api-master
```

### Step 2: Create and Activate Virtual Environment
Virtual environments are machine-specific and cannot be copied between computers. Create a fresh virtual environment using Python 3.12:
```powershell
# Remove old or copied venv if present
Remove-Item -Recurse -Force .\venv -ErrorAction SilentlyContinue

# Create new venv using Python 3.12 explicitly
& "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" -m venv venv

# Enable script execution and activate
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```
You should now see `(venv)` at the beginning of your prompt.

### Step 3: Install Dependencies
Install compatible `setuptools` (which provides `pkg_resources` and `distutils` shims) followed by project requirements:
```powershell
pip install "setuptools<70"
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (.env)
Ensure your `.env` file exists and has the correct PostgreSQL credentials:
```env
PYTH_SRVR=dev
MYSQL_ROOT_PASSWORD=root
FLASK_APP=manager.py
FLASK_ENV=development
FLASK_DEBUG=1
POSTGRE_CONNECTION_STRING=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/pos
```
*(Replace `YOUR_PASSWORD` with your PostgreSQL password, e.g., `vidhi123`, and port `5432` if different).*

### Step 5: Create the PostgreSQL Database
> [!IMPORTANT]
> Run this query inside **pgAdmin 4 (Query Tool)** or `psql`, **not** in PowerShell!

```sql
CREATE DATABASE "pos";
```

### Step 6: Initialize Database & Create Admin User
Run the Flask CLI commands in your PowerShell terminal to generate tables and create the admin user:
```powershell
# Ensure Flask knows the entrypoint
$env:FLASK_APP = "manager.py"

# 1. Create database tables and enable uuid-ossp extension
flask create-db

# 2. Create the initial admin user with full permissions
flask create-admin -e admin@pos.com -p "admin123" -n "Admin User" -m "9999999999"
```

### Step 7: Run the Application
Start the development server:
```powershell
flask run
```
The server will start at: `http://127.0.0.1:5000/`

---

## 3. Verification & Acceptance Criteria

1. **Verify Database in pgAdmin:**
   - In pgAdmin 4, select the `pos` database and open the Query Tool.
   - Note: Because `user` is a reserved PostgreSQL keyword, quote the table name:
     ```sql
     select * from "user";
     ```
   - You should see the admin user row with email `admin@pos.com`.

2. **API Login Check:**
   - Open your browser and visit: `http://127.0.0.1:5000/api/v1/login/`
   - Form loads successfully with HTTP 200.

3. **Admin Panel Access:**
   - Navigate to: `http://127.0.0.1:5000/admin/`
   - Log in using your created admin credentials:
     - **Email:** `admin@pos.com`
     - **Password:** `admin123`
   - Verify that you can view and manage Products, Orders, Users, and Retail Shops.

---

## 4. Problems Faced & How They Were Fixed

Since this project was originally built around 2017 with Python 3.6, several updates were required to run it smoothly on modern Python 3.12 on Windows:

### 1. Inactive Git Protocol & Git Not Installed
* **Issue:** `requirements.txt` had `-e git://github.com/...` and later `git+https://...`, which failed because GitHub retired unencrypted `git://`, and machines without `git.exe` in PATH aborted with `ERROR: Cannot find command 'git'`.
* **Fix:** Replaced with direct GitHub `.zip` archive download URL (`https://github.com/saurabh1e/flask_admin_impexp/archive/refs/heads/master.zip`). Pip installs it over HTTP without needing Git.

### 2. System Default Python 3.15 Incompatibility
* **Issue:** System default `python` pointed to an experimental Python 3.15 build (`C:\Python315\python.exe`), causing `ModuleNotFoundError: No module named 'sre_constants'`, broken C binary wheels for `psycopg2`, and `SyntaxWarning: 'return' in a 'finally' block`.
* **Fix:** Explicitly targeted installed **Python 3.12.10** executable to build the virtual environment.

### 3. `No module named 'pkg_resources'` (Setuptools 70+)
* **Issue:** Running `pip install setuptools` installed `setuptools>=84`, which completely removed `pkg_resources`. `flask_security` crashed on import, causing Flask CLI to fail to register `create-db` and `create-admin`.
* **Fix:** Pinned `setuptools<70` in requirements (`setuptools==69.5.1`), which includes `pkg_resources` and the `distutils` compatibility shim.

### 4. `ModuleNotFoundError: No module named 'distutils'`
* **Issue:** Python 3.12 removed `distutils` from the standard library (PEP 632), which `flask-marshmallow` and `marshmallow` 2.x relied on.
* **Fix:** `setuptools<70` provides a transparent `_distutils` shim that restores `distutils.version.LooseVersion`.

### 5. C-Build & MSVC Compilation Errors
* **Issue:** Older frozen dependencies (`cffi==1.9.1`, `pycrypto`, legacy `pygresql`) failed without Visual C++ Build Tools.
* **Fix:** Replaced with pre-compiled wheels direct from PyPI, specifically `psycopg2-binary`.

### 6. `TypeError: validate() got an unexpected keyword argument 'extra_validators'`
* **Issue:** Submitting forms like Register, Login, Forgot Password, or Confirm Account in the browser crashed with `TypeError: ...validate() got an unexpected keyword argument 'extra_validators'`.
* **Cause:** Modern `Flask-WTF 1.3.0` calls `form.validate(extra_validators=extra_validators)` inside `validate_on_submit()`. Older `Flask-Security 3.0` form `validate()` methods only accept `self`.
* **Fix:** Pinned `Flask-WTF<1.0` (`0.15.1`) in `requirements.txt` and updated custom form validate signatures to accept `*args, **kwargs`.


