# TaskFlow - Vulnerable Web Application

A simple web application with intentionally implemented vulnerabilities from OWASP Top 10:2021. It is a task/JIRA-like simple app.

## Start

```bash
pip install -r requirements.txt
python seeds.py
python run.py
```

Open http://localhost:5000 

## Test Users

All passwords match usernames:

- `alice` / `alice` - regular user (Development & Operations)
- `bob` / `bob` - regular user (Development & QA)
- `charlie` / `charlie` - regular user (QA & Operations)
- `testuser` / `testuser` - only in Development Team (for testing SQL Injection)
- `admin` / `admin` - system administrator

## Vulnerabilities

The application has 5 intentionally implemented vulnerabilities from OWASP Top 10:2021. All vulnerabilities are **active** by default, fixes are commented next to vulnerable code.

### 1. SQL Injection (A03:2021)

**Location:** `app/routes/task_routes.py` function `get_tasks()` (line ~25), `app/routes/user_routes.py` function `get_users()` (line ~23)

**Issue:** SQL queries are built using string concatenation without parameterization.

**How to exploit:**
1. Login as `testuser` / `testuser`
2. Go to `/tasks`
3. In search box, enter: `' OR '1'='1' OR '1'='1`
4. Click "Search"
5. You'll see all tasks from all teams, even though you should only see your own

**Fix:** Use parameterized queries via SQLAlchemy ORM (commented in code, quite long but works well)

---

### 2. Broken Access Control (A01:2021)

**Location:** `app/routes/task_routes.py` function `get_task()` (line ~162)

**Issue:** No check if user is a member of the tasks team before showing task details.

**How to exploit:**
1. Login as `bob` / `bob`
2. `bob` is NOT a member of Operations Team
3. Open in browser: `http://localhost:5000/api/tasks/7` (task from Operations Team)
4. You'll see a task you don't have access to

**Fix:** Check team membership before returning task (commented in code)

---

### 3. Broken Authentication (A07:2021)

**Location:** `app/routes/auth_routes.py` function `login()` (line ~56)

**Issue:**
No rate limiting - can try to guess password infinitely. Also, different error messages: "User not found" vs "Invalid password" — reveals if user exists

**How to exploit:**
1. Try logging in with wrong password 10 times in a row
2. All attempts pass (no blocking)
3. Different messages reveal which users exist in the system
4. Bruteforce to hack

**Fix:** Add rate limiting and use same error message (commented in code)

---

### 4. Cryptographic Failures (A02:2021)

**Location:** `app/__init__.py` function `handle_error()` (line ~110)

**Issue:** On error, full stack trace is returned with file paths and internal code structure.

**How to exploit:**
1. Send invalid request to API (e.g., POST to `/api/tasks` without data)
2. Check response - you'll see full stack trace with file paths

**Fix:** Never expose stack traces, always return generic error message (commented in code)

---

### 5. Security Misconfiguration (A05:2021)

**Location:** `app/__init__.py` (SECRET_KEY line ~38, CORS line ~48, security headers line ~92) and `app/auth.py` (JWT expiration line ~17)

**Issue:**
- Weak SECRET_KEY: `'TEST_SECRET_KEY'` - can forge JWT tokens
- JWT tokens live 365 days (too long)
- CORS open to all domains
- Security headers only in production

**How to exploit:**
1. Know the SECRET_KEY (it's in the code)
2. Decode your JWT token
3. Change `role` to `app_admin`
4. Re-sign token - get admin rights!

**Fix:** Strong secret, short tokens, restricted CORS, always security headers (commented in code)

