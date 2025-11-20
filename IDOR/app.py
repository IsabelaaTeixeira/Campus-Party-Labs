from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'insecure-secret-key-for-lab'

# Load users from JSON file
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

# Save users to JSON file
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

# Initialize with some default users
def init_users():
    if not os.path.exists('users.json'):
        users = {
            'admin': {
                'password': 'admin123',
                'email': 'admin@company.com',
                'ssn': '123-45-6789',
                'phone': '+1-555-0100',
                'address': '123 Admin Street, NY',
                'credit_card': '4532-1111-2222-3333',
                'picture': 'admin.jpg'
            },
            'john': {
                'password': 'john123',
                'email': 'john.doe@email.com',
                'ssn': '987-65-4321',
                'phone': '+1-555-0101',
                'address': '456 User Avenue, CA',
                'credit_card': '4532-4444-5555-6666',
                'picture': 'john.jpg'
            },
            'sarah': {
                'password': 'sarah123',
                'email': 'sarah.smith@email.com',
                'ssn': '555-12-3456',
                'phone': '+1-555-0102',
                'address': '789 Customer Blvd, TX',
                'credit_card': '4532-7777-8888-9999',
                'picture': 'sarah.jpg'
            },
            'mike': {
                'password': 'mike123',
                'email': 'mike.johnson@email.com',
                'ssn': '111-22-3333',
                'phone': '+1-555-0103',
                'address': '321 Guest Lane, FL',
                'credit_card': '4532-0000-1111-2222',
                'picture': 'mike.jpg'
            }
        }
        save_users(users)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = load_users()
        
        # Vulnerable login - no proper security
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('profile', username=username))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/profile/<username>')
def profile(username):
    # IDOR VULNERABILITY: No access control check!
    # Anyone can view any profile by changing the username in the URL
    # There's no check if session['username'] == username
    
    if 'username' not in session:
        return redirect(url_for('login'))
    
    users = load_users()
    
    if username not in users:
        return "User not found", 404
    
    user_data = users[username]
    
    return render_template('profile.html', 
                         username=username,
                         user=user_data,
                         logged_in_as=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_users()
    print("=" * 60)
    print("IDOR Vulnerable Web Application - Pentesting Lab")
    print("=" * 60)
    print("\nDefault User Accounts:")
    print("  Username: admin  | Password: admin123")
    print("  Username: john   | Password: john123")
    print("  Username: sarah  | Password: sarah123")
    print("  Username: mike   | Password: mike123")
    print("\nVulnerability: IDOR on /profile/<username>")
    print("After login, change the username in the URL to access other profiles!")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
