# Example Book API 
This is a exploritory effort to understand how APIs work in python. There are additional sub-topics explored during the effort.
Please review the documents in sub folder "docs" for more information.

## API Resources from exploration:
1. https://www.altexsoft.com/blog/what-is-api-definition-types-specifications-documentation/
    a. There is a good video under the above link: https://www.youtube.com/watch?v=yBZO5Rb4ibo
2. https://blog.postman.com/how-to-build-an-api-in-python/
3. Flask API
    a. https://flask.palletsprojects.com/en/stable/api/#

## API Concepts:
### Structure:
- Overall Structure
    - An API works under a Client(Requestor) - Server (Processor/Actor) model.
    - What causes a request:
        1. A web-application can act based on user interaction or input, then pass info back if required.
        2. System-to-system interactions can occur for systems working together.
            a. Kafka broker, producer, consumer APIs
            b. Spark worker APIs
        3. 
- Storing Info
    - Option 1: Python class objects can be used to hold the contents or define the structure of information for use on the backend.
    - Option 2: The info can be stored in a database system.
- CURL Commands:
    - The base commands are GET, POST, PUT, and DELETE (for the -X cURL command)
    - However there are other types of cURL commands for file uploads, authentication, etc.
    - There are tons of additional modifiers for doing stuff like saving to files, adding headers, etc.
    - Resources:
        - https://blog.hubspot.com/website/curl-command#curl-syntax
        - https://www.hostinger.com/tutorials/curl-command 
![alt text](image.png)
- Client Code (more info in docs\api_interactions-examples.md)
    - You can create a client for wrapping up complex commands or actions for users.
    - See book_client.py
- Decorators
    - Useful Github Curated List: https://github.com/lord63/awesome-python-decorator
    - Basics: https://www.kdnuggets.com/8-built-in-python-decorators-to-write-elegant-code
    - functtools.wraps deep-div: https://jacobpadilla.com/articles/functools-deep-dive 

## Future Learning:
1. FastAPI vs. Flask vs. Django vs. other options
2. API Key Authentication
3. B: Encryption of sending data as well as file uploads.
4. How to scale API request vs response of Client-Server structure?
    a. Via a middle man load balancer, or maybe kafka topics?

## Other Learnings:
### Building/Running an Python Application
- Basics:
    - Create an app.py file for initializing the API or app.
- Ways to Run (more info: docs\python-api-guide.md)
    - Direct Execution for local development
        - On Command Line under Venv or Conda: python app.py
        - default is access via http://localhost:5000
        - CURL Commands:
            - GET all books
            - curl http://localhost:5000/books
            - GET a specific book by ID
            - curl http://localhost:5000/books/1
    - Gunicorn for Production Hosting
        - a python based WSGI hosting package
    - Docker File
        - For scalable execution for API load. Still using Guincorn or other web-engine.
    - Cloud Platform (can use docker on cloud)
        - Docker, AWS Elastic Beanstalk, Google Cloud Run, Heroku

