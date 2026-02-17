LINK: https://github.com/akiracrying/csb-project

Installation instructions:
1. Install Python dependencies: pip install -r requirements.txt
2. Initialize database with test data: python seeds.py
3. Run the application: python run.py
4. Open http://localhost:5000 in browser

How to find vulnerabilities and fixes in code:
All vulnerable code blocks and their fixes are marked with comments in the source files.
Vulnerable code: 

 # --- VULN: FLAW n - ... ---  
 ...  
 # --- END VULN ---

Fixed code:      

 # --- FIX: FLAW n - ... ---   
 ... 
 # --- END FIX ---

To apply a fix comment out the VULN block and uncomment the FIX block below it

To revert to vulnerable version uncomment the VULN block and comment out the FIX block

FLAW 1:
Source: https://github.com/akiracrying/csb-project/blob/main/app/routes/task_routes.py#L26

The application is vulnerable to SQL injection in the task search functionality. The get_tasks function in app/routes/task_routes.py constructs SQL queries using string concatenation without parameterization. When a user enters a search query, it is directly inserted into the SQL query string on line 26: query = f"SELECT * FROM tasks WHERE (title LIKE '%{search}%' OR description LIKE '%{search}%')". This allows an attacker to inject malicious SQL code.

An attacker can exploit this by logging in as testuser and entering a payload like ' OR '1'='1' OR '1'='1 in the search box. This bypasses the team-based access control and returns all tasks from all teams, even though the user should only see tasks from their own team. Screenshots flaw-1-before-1.png and flaw-1-after-1.png demonstrate this vulnerability.

The fix is to use parameterized queries through SQLAlchemy ORM instead of string concatenation. The fix is commented out in the code starting at line 52. Instead of building raw SQL strings, the code should use Task.query.filter() with SQLAlchemy's like() method, which automatically handles parameterization and prevents SQL injection.

FLAW 2:
Source: https://github.com/akiracrying/csb-project/blob/main/app/routes/task_routes.py#L124

The application suffers from broken access control in the get_task function. When a user requests a specific task by ID through the /api/tasks/<task_id> endpoint, the application does not verify whether the user is a member of the team that owns the task. The function on line 119 retrieves the task on line 120 and immediately returns it without checking team membership.

An attacker can exploit this by logging in as bob, who is not a member of the Operations Team and directly accessing http://localhost:5000/api/tasks/7 which belongs to Operations Team. The application will return the task details including comments, even though bob should not have access to this information. Screenshot flaw-2-after-1.png shows successful unauthorized access.

The fix is to check team membership before returning the task. The fix is commented out starting at line 128. The code should query the TeamMember table to verify that the current user is a member of the task's team, or is an app_admin. If the user is not authorized, the function should return a 403 Forbidden error instead of the task data.

FLAW 3:
Source: https://github.com/akiracrying/csb-project/blob/main/app/routes/auth_routes.py#L55

The login function has two critical authentication flaws. First, there is no rate limiting on the login endpoint (line 55), allowing unlimited login attempts. Second, the function returns different error messages for different failure scenarios: "User not found" on line 73 when the username does not exist and "Invalid password" on line 76 when the username exists but the password is wrong. This enables user enumeration attacks.

An attacker can exploit this by attempting to log in with various usernames. If they receive "User not found", the username does not exist. If they receive "Invalid password", the username exists and they can proceed to brute force the password. Additionally, without rate limiting, an attacker can make unlimited login attempts without being blocked. Screenshots flaw-3-before-1.png, flaw-3-before-2.png and flaw-3-before-3.png demonstrate these issues.

The fix requires two changes. First, add rate limiting using the @limiter.limit decorator, which is commented out on line 60. Second, use a generic error message for both cases to prevent user enumeration. The fix is commented out starting at line 80, which returns "Invalid username or password" for both scenarios, making it impossible to distinguish between non-existent users and wrong passwords.

FLAW 4:
Source: https://github.com/akiracrying/csb-project/blob/main/app/__init__.py#L123

The application exposes sensitive information through error handling. The handle_error function in app/__init__.py returns full stack traces with file paths and internal code structure when an error occurs. On line 124, when DEBUG mode is enabled, the function returns both the error message and the complete traceback, which includes absolute file paths like C:\MyData\Programms\Conda\Lib\site-packages\flask\app.py.

An attacker can exploit this by sending invalid requests to the API, such as POST requests to non-existent endpoints or with malformed data. The server responds with detailed stack traces that reveal the internal structure of the application, file system paths and potentially sensitive information about the deployment environment. Screenshot flaw-4-before-1.png shows a stack trace exposed in the browser console.

The fix is to never expose stack traces in responses, regardless of DEBUG mode. The fix is commented out on line 131, which always returns a generic "Internal server error" message. Stack traces should only be logged server-side for debugging purposes, never sent to the client. This prevents information disclosure while still allowing developers to debug issues through server logs.

FLAW 5:
Source: https://github.com/akiracrying/csb-project/blob/main/app/__init__.py#L37 and https://github.com/akiracrying/csb-project/blob/main/app/auth.py#L15

The application has multiple security misconfigurations. First, the SECRET_KEY is hardcoded to 'TEST_SECRET_KEY' on line 37 of app/__init__.py, making it trivial to forge JWT tokens. Second, JWT tokens have an expiration time of 365 days on line 15 of app/auth.py, which is excessively long. Third, CORS is configured to allow all origins on line 53 of app/__init__.py with CORS(app). Fourth, security headers are only set in production mode, not in development (line 102 of app/__init__.py).

An attacker can exploit these misconfigurations by knowing the weak SECRET_KEY from the source code, decoding a JWT token, modifying the role field to app_admin and re-signing the token with the known secret. Since tokens last 365 days, a compromised token remains valid for a very long time. The open CORS policy allows any website to make requests to the API. Screenshots flaw-5-before-1.png, flaw-5-before-2.png, flaw-5-before-3.png and flaw-5-after-1.png demonstrate these vulnerabilities.

The fix requires multiple changes. For SECRET_KEY, use a strong random secret from environment variables or generate one securely, as shown in the commented fix on line 41. For JWT expiration, reduce the token lifetime to 1 hour and implement refresh tokens, as commented on line 19 of app/auth.py. For CORS, restrict to specific trusted origins instead of allowing all, as shown in the commented fix on line 57. For security headers, always set them regardless of DEBUG mode, as shown in the commented fix starting at line 108.


