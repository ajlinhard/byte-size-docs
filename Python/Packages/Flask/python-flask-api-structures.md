
# Flask Basics

## Table of Contents

### 1. [Flask Basics](#flask-basics)
   - Basic Flask app implementation
   - Installation requirements
   - Project structure

### 2. [Flask App as a Class](#flask-app-as-a-class)
   - Class-based approach to Flask applications
   - Advantages of using classes
   - Route configuration methods

## 3. [Approaches to URL Routes](#approaches-to-url-routes)
   #### 3.1 [`@app.route` Decorator](#1-approute-decorator)
   - Most common approach
   - Declarative style
   
   #### 3.2 [`add_url_rule()` Method](#2-add_url_rule-method)
   - Programmatic approach
   - Dynamic route registration
   
   #### 3.3 [`add_resource()` Method](#3-add_resource-method)
   - Flask-RESTful extension
   - Class-based resources
   - When to use each approach

### 4. [POST Request Payloads](#post-request-payloads)
   - Reading different content types
   - Form data handling
   - JSON data processing
   - File uploads
   - Complete implementation example

### 5. [Ways to Send Requests](#ways-to-send-request)
   #### 5.1 [Using HTML Forms](#1-using-html-forms)
   #### 5.2 [Using JavaScript with Fetch API](#2-using-javascript-with-fetch-api)
   #### 5.3 [Using Python's Requests Library](#3-using-pythons-requests-library)
   #### 5.4 [Using cURL from the Command Line](#4-using-curl-from-the-command-line)
   #### 5.5 [Using Postman (GUI Tool)](#5-using-postman-gui-tool)
   - Best practices for POST requests

---
Below I will show you the basics of implementing a Flask app. Flask is a lightweight web framework for Python that's great for beginners and small to medium-sized applications.

Here's a simple implementation to get you started:

```python
from flask import Flask, render_template, request, redirect, url_for

# Create the Flask application instance
app = Flask(__name__)

# Define a basic route for the homepage
@app.route('/')
def home():
    return 'Hello, World! This is my Flask app.'

# Route with a parameter
@app.route('/greet/<name>')
def greet(name):
    return f'Hello, {name}!'

# Route with HTML template
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# Route handling form submission
@app.route('/submit', methods=['GET', 'POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form.get('name')
        return redirect(url_for('greet', name=name))
    return render_template('form.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
```

To make this work properly, you'll need to:

1. Install Flask: `pip install flask`

2. Create a folder called `templates` in the same directory as your Python file

3. Create HTML templates:
   - `welcome.html` - A simple welcome page
   - `form.html` - A form that submits to the `/submit` route

Here's a simple structure for your project:

```
my_flask_app/
├── app.py               # Your main Flask application file
├── static/              # For CSS, JavaScript, images
│   └── style.css
└── templates/           # HTML templates
    ├── welcome.html
    └── form.html
```

# Flask App as a Class
Yes, you can absolutely structure your Flask application using a class-based approach. This can make your code more organized, especially for larger applications. Here's how you could rewrite the Flask app as a class:

```python
from flask import Flask, render_template, request, redirect, url_for

class FlaskAppWrapper:
    def __init__(self, name):
        self.app = Flask(name)
        self.configure_routes()
        
    def configure_routes(self):
        # Define all your routes
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/greet/<name>', 'greet', self.greet)
        self.app.add_url_rule('/welcome', 'welcome', self.welcome)
        self.app.add_url_rule('/submit', 'submit_form', self.submit_form, methods=['GET', 'POST'])
    
    def home(self):
        return 'Hello, World! This is my Flask app.'
    
    def greet(self, name):
        return f'Hello, {name}!'
    
    def welcome(self):
        return render_template('welcome.html')
    
    def submit_form(self):
        if request.method == 'POST':
            name = request.form.get('name')
            return redirect(url_for('greet', name=name))
        return render_template('form.html')
    
    def run(self, debug=True):
        self.app.run(debug=debug)

# Create and run the application
if __name__ == '__main__':
    flask_app = FlaskAppWrapper(__name__)
    flask_app.run(debug=True)
```

This class-based approach offers several advantages:

1. Better organization of your code
2. Easier to extend functionality
3. More maintainable as your application grows
4. Makes testing easier, as you can instantiate your app in test files

Note that within class methods that handle routes, you access Flask's request object directly from the imported module, not through `self`, since it's a global object provided by Flask.

---
# Approaches to URL Routes
These three approaches represent different ways to establish URL routes in Flask, with varying levels of abstraction and flexibility. Let's break down each approach:

## 1. `@app.route` Decorator

```python
@app.route('/users', methods=['GET'])
def get_users():
    return 'List of users'
```

**Characteristics:**
- Most common and straightforward approach
- Declarative style that directly associates a function with a URL pattern
- Simple to read and understand
- Built into Flask's core functionality
- Good for simple applications and quick development

## 2. `add_url_rule()` Method

```python
def get_users():
    return 'List of users'
    
app.add_url_rule('/users', 'get_users', get_users, methods=['GET'])
```

**Characteristics:**
- More programmatic approach that accomplishes the same thing as `@app.route`
- Gives you the ability to register routes dynamically at runtime
- Useful when you need to add routes conditionally or based on configuration
- Allows you to separate the function definition from route registration
- Takes parameters: rule (URL pattern), endpoint name, view function, and options

## 3. `add_resource()` Method

```python
from flask_restful import Api, Resource

api = Api(app)

class UserResource(Resource):
    def get(self):
        return {'users': ['user1', 'user2']}
    
    def post(self):
        return {'status': 'user created'}, 201

api.add_resource(UserResource, '/users')
```

**Characteristics:**
- Part of Flask-RESTful extension, not core Flask
- Class-based approach that organizes HTTP methods as class methods
- Automatically maps HTTP methods (GET, POST, etc.) to corresponding methods in your Resource class
- Better suited for building RESTful APIs
- Provides built-in features like request parsing, content negotiation, and response formatting
- Encourages more structured organization of related endpoints

## When to use each approach:

- **`@app.route`**: Use for simple applications, when readability is important, or for quick prototyping.
  
- **`add_url_rule()`**: Use when you need to register routes programmatically, such as in factories, blueprints, or when routes depend on configuration values.

---
# POST Request Payloads
Reading the payload of a Flask POST request depends on the content type of the request. Here are the most common ways to access POST request data:

```python
from flask import request

# For form data (Content-Type: application/x-www-form-urlencoded)
form_data = request.form
value = request.form.get('key')  # Get a specific value (returns None if key doesn't exist)
value = request.form['key']      # Also gets a value but raises KeyError if key doesn't exist

# For JSON data (Content-Type: application/json)
json_data = request.json         # Returns parsed JSON data
value = request.json.get('key')  # Get a specific value

# For raw data (any Content-Type)
raw_data = request.data          # Raw binary data from the request body as bytes
text_data = request.data.decode('utf-8')  # Convert bytes to string if needed

# For file uploads (Content-Type: multipart/form-data)
file = request.files['file_key']
filename = file.filename
file.save('/path/to/save/' + filename)

# For URL parameters (query string)
query_param = request.args.get('param')
```

Here's a complete example in a class-based Flask app:

```python
from flask import Flask, request, jsonify

class FlaskAppWrapper:
    def __init__(self, name):
        self.app = Flask(name)
        self.configure_routes()
        
    def configure_routes(self):
        self.app.add_url_rule('/api/data', 'receive_data', 
                             self.receive_data, methods=['POST'])
    
    def receive_data(self):
        # Check content type header
        content_type = request.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # Handle JSON data
            data = request.json
            return jsonify({
                'message': 'JSON received',
                'data': data,
                'name': data.get('name', 'No name provided')
            })
            
        elif 'application/x-www-form-urlencoded' in content_type:
            # Handle form data
            data = request.form
            return jsonify({
                'message': 'Form data received',
                'name': data.get('name', 'No name provided')
            })
            
        elif 'multipart/form-data' in content_type:
            # Handle file uploads and form data
            files = request.files
            form_data = request.form
            
            file_info = {}
            if 'file' in files:
                file = files['file']
                file_info = {
                    'filename': file.filename,
                    'content_type': file.content_type,
                    'size': len(file.read())
                }
                file.seek(0)  # Reset file pointer after reading
                
            return jsonify({
                'message': 'Multipart data received',
                'form_data': {k: v for k, v in form_data.items()},
                'file_info': file_info
            })
            
        else:
            # Handle raw data
            raw_data = request.data
            return jsonify({
                'message': 'Raw data received',
                'data_size': len(raw_data),
                'data_preview': raw_data[:100].decode('utf-8', errors='replace')
            })
    
    def run(self, debug=True):
        self.app.run(debug=debug)

# Create and run the application
if __name__ == '__main__':
    flask_app = FlaskAppWrapper(__name__)
    flask_app.run(debug=True)
```

This implementation handles different types of POST request payloads and shows you how to access each type of data. You can adapt this to your specific needs based on what kind of payload you're expecting.

---
# Ways to send request:
Making a POST request to a Flask app can be done in several ways. Here are the most common methods:

## 1. Using HTML Forms

```html
<form action="/api/data" method="POST">
  <input type="text" name="username" placeholder="Username">
  <input type="password" name="password" placeholder="Password">
  <button type="submit">Submit</button>
</form>
```

## 2. Using JavaScript with Fetch API

```javascript
// Form data
fetch('/api/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    'username': 'user123',
    'password': 'secretpassword'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// JSON data
fetch('/api/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'user123',
    password: 'secretpassword'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 3. Using Python's Requests Library

```python
import requests

# Form data
response = requests.post(
    'http://localhost:5000/api/data',
    data={
        'username': 'user123',
        'password': 'secretpassword'
    }
)
print(response.json())

# JSON data
response = requests.post(
    'http://localhost:5000/api/data',
    json={
        'username': 'user123',
        'password': 'secretpassword'
    }
)
print(response.json())

# File upload
files = {'file': open('example.txt', 'rb')}
response = requests.post(
    'http://localhost:5000/api/upload',
    files=files,
    data={'description': 'My file description'}
)
print(response.json())
```

## 4. Using cURL from the Command Line

```bash
# Form data
curl -X POST http://localhost:5000/api/data \
  -d "username=user123&password=secretpassword"

# JSON data
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -d '{"username":"user123","password":"secretpassword"}'

# File upload
curl -X POST http://localhost:5000/api/upload \
  -F "file=@example.txt" \
  -F "description=My file description"
```

## 5. Using Postman (GUI Tool)

1. Open Postman
2. Set the request type to POST
3. Enter your URL (e.g., http://localhost:5000/api/data)
4. Select the Body tab
5. Choose your data format (form-data, x-www-form-urlencoded, raw JSON, etc.)
6. Add your key-value pairs
7. Click Send

When making POST requests, remember to:

1. Use the correct Content-Type header for your data format
2. Format your data according to the expected input of your Flask endpoint
3. Handle CSRF tokens if your Flask app uses them (common in Flask-WTF)
4. Check for any authentication requirements

  
- **`add_resource()`**: Use when building RESTful APIs where you want to group related HTTP methods (GET, POST, PUT, DELETE) for a resource in a single class, or when you need the additional features of Flask-RESTful.
