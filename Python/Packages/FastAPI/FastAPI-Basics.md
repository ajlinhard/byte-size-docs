# FastAPI Walkthrough

I'd be happy to walk you through a basic example of FastAPI and explain its key components for setting up an API.

FastAPI is a modern, high-performance web framework for building APIs with Python. It's known for being fast, easy to use, and having excellent automatic documentation features.

## Basic FastAPI Example

Let's create a simple API with FastAPI:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# Initialize the FastAPI application
app = FastAPI(title="Sample API", description="A simple API example")

# Define a data model
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# Create a mock database
items_db = {}

# Create a GET endpoint that returns all items
@app.get("/items/", response_model=List[Item])
async def get_items():
    return list(items_db.values())

# Create a GET endpoint that returns a specific item by ID
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

# Create a POST endpoint to add an item
@app.post("/items/", response_model=Item, status_code=201)
async def create_item(item: Item):
    if item.id in items_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    items_db[item.id] = item
    return item

# Create a PUT endpoint to update an item
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item
    return item

# Create a DELETE endpoint to remove an item
@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return None

# Add a root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI example!"}

# Run the API with: uvicorn main:app --reload
```

## Key Components of FastAPI

### 1. Application Initialization

```python
app = FastAPI(title="Sample API", description="A simple API example")
```

This creates a FastAPI application instance with metadata that will appear in the automatically generated documentation.

### 2. Data Models with Pydantic

```python
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
```

Pydantic models define the structure of your request and response data. They provide:
- Automatic validation
- Type checking
- Documentation generation
- Default values

### 3. Path Operations (Routes)

```python
@app.get("/items/")
@app.post("/items/")
@app.get("/items/{item_id}")
```

These decorators define your API endpoints with:
- HTTP method (GET, POST, PUT, DELETE)
- Path (URL route)
- Path parameters (like `item_id`)

### 4. Function Parameters and Request Data

FastAPI automatically handles:
- Path parameters: `item_id: int` in the function parameters
- Query parameters: `?skip=0&limit=10` automatically mapped to function parameters
- Request body: Automatically parsed from JSON to your Pydantic model

### 5. Response Models

```python
@app.get("/items/", response_model=List[Item])
```

The `response_model` parameter:
- Validates the response data
- Filters out extra data not in the model
- Generates response documentation
- Handles type conversion

### 6. Status Codes and Error Handling

```python
@app.post("/items/", status_code=201)
```

```python
from fastapi import HTTPException

if item_id not in items_db:
    raise HTTPException(status_code=404, detail="Item not found")
```

### 7. Running the Application

To run your FastAPI application, you use Uvicorn, an ASGI server:

```
uvicorn main:app --reload
```

Where:
- `main` is the name of your Python file (main.py)
- `app` is the FastAPI instance in your code
- `--reload` enables auto-reload during development

### 8. Automatic Documentation

FastAPI automatically generates API documentation:
- Swagger UI: `/docs` - Interactive documentation
- ReDoc: `/redoc` - Alternative documentation UI

## Getting Started Steps

1. Install FastAPI: `pip install fastapi uvicorn`
2. Create a Python file (e.g., `main.py`) with your API code
3. Run with Uvicorn: `uvicorn main:app --reload`
4. Access your API at http://localhost:8000
5. View the documentation at http://localhost:8000/docs
