# IDOR Vulnerable Web Application - Pentesting Lab

## Overview
This is a deliberately vulnerable web application designed for educational purposes to demonstrate **IDOR (Insecure Direct Object Reference)** vulnerability.

## Vulnerability Description
The application has an **IDOR vulnerability** in the profile page (`/profile/<username>`). After authentication, users can access ANY user's profile by simply changing the username in the URL, exposing sensitive personal information.

## Setup Instructions

### Requirements
- Python 3.x
- Flask

### Installation

1. Install Flask:
```bash
pip install flask
```

2. Run the application:
```bash
python app.py
```

3. Access the application:
```
http://localhost:5000
```

## Test Accounts

| Username | Password  |
|----------|-----------|
| admin    | admin123  |
| john     | john123   |
| thiago   | oreo      |
| mike     | mike123   |

## Exploitation Steps

1. **Login** with any account (e.g., `john` / `john123`)
2. After login, you'll be redirected to: `http://localhost:5000/profile/john`
3. **Change the username** in the URL to another user:
   - `http://localhost:5000/profile/admin`
   - `http://localhost:5000/profile/sarah`
   - `http://localhost:5000/profile/mike`
4. **Observe** that you can view other users' sensitive information including:
   - Email address
   - Phone number
   - Social Security Number (SSN)
   - Credit card information
   - Physical address

## The Vulnerability

### Vulnerable Code (app.py):
```python
@app.route('/profile/<username>')
def profile(username):
    # IDOR VULNERABILITY: No access control check!
    # Anyone can view any profile by changing the username in the URL
    # There's no check if session['username'] == username
    
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # ... displays user data based on URL parameter
```

### Why It's Vulnerable:
- The application only checks if a user is logged in
- It does NOT verify if the logged-in user has permission to view the requested profile
- Access control is missing: `session['username'] != username` is never checked

## Remediation

To fix this vulnerability, add proper access control:

```python
@app.route('/profile/<username>')
def profile(username):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # FIX: Check if the logged-in user matches the requested profile
    if session['username'] != username:
        return "Access Denied: You can only view your own profile", 403
    
    # ... rest of the code
```

## Learning Objectives

Students should learn:
1. What IDOR vulnerabilities are
2. How to identify IDOR in web applications
3. The impact of missing access control checks
4. How to exploit IDOR vulnerabilities
5. Proper remediation techniques

## Warning

⚠️ **THIS APPLICATION IS INTENTIONALLY VULNERABLE**

- Do NOT deploy this in production
- Use only in isolated lab environments
- This is for educational purposes only

## License

This lab is provided for educational purposes. Use responsibly.

