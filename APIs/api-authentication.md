# Comprehensive API User Authentication Guide

## 1. JWT (JSON Web Token) Authentication

### User Model and Database Setup
```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt
import datetime
import os

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Secret key for JWT - use environment variable in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'development_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class AuthManager:
    @staticmethod
    def generate_token(user):
        """Generate JWT token for user"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def decode_token(token):
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token, 
                app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token

class AuthController:
    @staticmethod
    def register():
        """User registration endpoint"""
        data = request.get_json()
        
        # Check if user already exists
        existing_user = User.query.filter_by(
            username=data['username']
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(
            data['password']
        ).decode('utf-8')
        
        # Create new user
        new_user = User(
            username=data['username'],
            password=hashed_password,
            email=data['email']
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token
        token = AuthManager.generate_token(new_user)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token
        }), 201

    @staticmethod
    def login():
        """User login endpoint"""
        data = request.get_json()
        
        user = User.query.filter_by(
            username=data['username']
        ).first()
        
        if user and bcrypt.check_password_hash(
            user.password, 
            data['password']
        ):
            # Generate token
            token = AuthManager.generate_token(user)
            
            return jsonify({
                'message': 'Login successful',
                'token': token
            }), 200
        
        return jsonify({
            'error': 'Invalid credentials'
        }), 401

def token_required(f):
    """Decorator to require valid token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
        
        if not token:
            return jsonify({
                'error': 'Authentication token is missing'
            }), 401
        
        # Decode token
        payload = AuthManager.decode_token(token)
        
        if not payload:
            return jsonify({
                'error': 'Invalid or expired token'
            }), 401
        
        # Attach user information to request
        current_user = User.query.get(payload['user_id'])
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# API Routes
@app.route('/register', methods=['POST'])
def user_registration():
    return AuthController.register()

@app.route('/login', methods=['POST'])
def user_login():
    return AuthController.login()

@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({
        'message': f'Hello {current_user.username}, this is a protected route'
    })
```

## 2. Token Storage Strategies

### Frontend (JavaScript) Example
```javascript
// Token Storage in Browser
class TokenManager {
    // Store token in localStorage
    static storeToken(token) {
        localStorage.setItem('api_token', token);
    }

    // Retrieve token
    static getToken() {
        return localStorage.getItem('api_token');
    }

    // Remove token (logout)
    static clearToken() {
        localStorage.removeItem('api_token');
    }

    // Automatic token inclusion in requests
    static configureAxios() {
        axios.interceptors.request.use(
            config => {
                const token = TokenManager.getToken();
                if (token) {
                    config.headers['Authorization'] = `Bearer ${token}`;
                }
                return config;
            },
            error => Promise.reject(error)
        );
    }
}

// Usage
function login(username, password) {
    axios.post('/login', { username, password })
        .then(response => {
            TokenManager.storeToken(response.data.token);
            // Redirect to protected route
        });
}
```

### Python Persistent Token Storage
```python
import sqlite3
import hashlib

class TokenStorage:
    def __init__(self, db_path='tokens.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                user_id INTEGER PRIMARY KEY,
                token TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def store_token(self, user_id, token):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO tokens (user_id, token) 
            VALUES (?, ?)
        ''', (user_id, token))
        self.conn.commit()
    
    def get_token(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT token FROM tokens WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
```

## Key Authentication Concepts

### Authentication Workflow
1. User registers
2. Credentials validated
3. JWT token generated
4. Token stored client-side
5. Token sent with subsequent requests
6. Server validates token

### Security Best Practices
- Use HTTPS
- Store tokens securely
- Implement token expiration
- Use strong, environment-specific secret keys
- Hash passwords
- Implement token refresh mechanism

### Libraries and Tools
- `PyJWT` for token generation/validation
- `Flask-Bcrypt` for password hashing
- `SQLAlchemy` for database management
```

Let me break down the key components of API authentication:

### 1. Authentication Strategies
- JWT (JSON Web Tokens)
- Session-based authentication
- OAuth
- API Keys

### 2. Core Authentication Components
- User model
- Password hashing
- Token generation
- Token validation
- Protected routes

### 3. Security Considerations
- Never store plain-text passwords
- Use strong hashing algorithms
- Implement token expiration
- Secure token transmission
- Validate and sanitize inputs

### Recommended Approach
1. Use JWT for stateless authentication
2. Implement secure token storage
3. Validate tokens on each request
4. Use HTTPS
5. Implement proper error handling

Would you like me to elaborate on any specific aspect of API authentication or explain more about token management?

Key takeaways:
- Authentication is about verifying user identity
- Tokens provide a secure way to maintain authentication state
- Always prioritize security in implementation