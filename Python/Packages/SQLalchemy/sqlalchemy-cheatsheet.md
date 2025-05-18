# SQLAlchemy Cheatsheet

SQL Alchemy is a framework for easily allowing your system to work with different types of databases using the same schema definitions directly in python. A vary useful package which is greate out of the box and many advance techniques to learn long term.

### Documentation and Tutorials
- [Offical SQL Alchemy Core](https://docs.sqlalchemy.org/en/20/core/index.html)
- [Offical SQL Alchemy ORM (Object-Relational Mapping)](https://docs.sqlalchemy.org/en/20/orm/index.html)

### SQLAlchemy Cheatsheet - Table of Contents

- [Installation](#installation)
- [Basic Setup](#basic-setup)
- [Defining Models/Schemas](#defining-modelsschemas)
  - [Basic Model](#basic-model)
  - [Common Column Types](#common-column-types)
  - [Column Constraints and Defaults](#column-constraints-and-defaults)
- [Database Relationships](#database-relationships)
  - [One-to-Many Relationship](#one-to-many-relationship)
  - [Many-to-Many Relationship](#many-to-many-relationship)
  - [One-to-One Relationship](#one-to-one-relationship)
  - [Self-Referential Relationship](#self-referential-relationship)
  - [Advanced Relationship Options](#advanced-relationship-options)
- [Creating Tables](#creating-tables)
- [CRUD Operations](#crud-operations)
  - [Create (Insert)](#create-insert)
  - [Read (Query)](#read-query)
  - [Update](#update)
  - [Delete](#delete)
- [Transactions](#transactions)
- [Alembic for Migrations](#alembic-for-migrations)
- [Using SQLAlchemy 2.0 Style](#using-sqlalchemy-20-style)

## Installation

```python
pip install sqlalchemy
```

## Basic Setup

```python
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

# Create engine
engine = create_engine('postgresql://username:password@localhost/dbname')
# For SQLite
# engine = create_engine('sqlite:///database.db')

# Create declarative base class
Base = declarative_base()

# Create session factory
Session = sessionmaker(bind=engine)
session = Session()
```

## Defining Models/Schemas

### Basic Model

```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True)
    age = Column(Integer)
    
    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"
```

### Common Column Types

```python
from sqlalchemy import (Boolean, Date, DateTime, Float, JSON, 
                        LargeBinary, Numeric, Text, Time, ARRAY)

class ModelWithTypes(Base):
    __tablename__ = 'model_types'
    
    id = Column(Integer, primary_key=True)
    boolean_value = Column(Boolean, default=False)
    date_value = Column(Date)
    datetime_value = Column(DateTime)
    float_value = Column(Float)
    json_value = Column(JSON)
    binary_data = Column(LargeBinary)
    decimal_value = Column(Numeric(10, 2))  # precision, scale
    text_value = Column(Text)
    time_value = Column(Time)
    # PostgreSQL specific
    array_value = Column(ARRAY(Integer))
```

### Column Constraints and Defaults

```python
from sqlalchemy import CheckConstraint, UniqueConstraint, default, func

class ConstrainedModel(Base):
    __tablename__ = 'constrained_models'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    status = Column(String(20), default='active')
    
    # Table-level constraints
    __table_args__ = (
        UniqueConstraint('field1', 'field2', name='unique_field_combination'),
        CheckConstraint('char_count > 5', name='min_char_count'),
    )
```

## Database Relationships

### One-to-Many Relationship

```python
class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    
    # One department has many employees
    employees = relationship("Employee", back_populates="department")
    
class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    # Many employees belong to one department
    department = relationship("Department", back_populates="employees")
```

### Many-to-Many Relationship

```python
# Association table for many-to-many relationship
student_course = Table('student_course', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    
    # Many students take many courses
    courses = relationship("Course", secondary=student_course, back_populates="students")
    
class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    
    # Many courses have many students
    students = relationship("Student", secondary=student_course, back_populates="courses")
```

### One-to-One Relationship

```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    
    # One user has one profile
    profile = relationship("Profile", uselist=False, back_populates="user")
    
class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    bio = Column(Text)
    
    # One profile belongs to one user
    user = relationship("User", back_populates="profile")
```

### Self-Referential Relationship

```python
class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    manager_id = Column(Integer, ForeignKey('employees.id'))
    
    # Self-referential relationship
    manager = relationship("Employee", remote_side=[id], backref="subordinates")
```

### Advanced Relationship Options

```python
# Cascade delete
parent = relationship("Child", cascade="all, delete-orphan")

# Lazy loading options
items = relationship("Item", lazy="select")  # Default, loads when accessed
items = relationship("Item", lazy="joined")  # Eager loading with JOIN
items = relationship("Item", lazy="subquery")  # Eager loading with subquery
items = relationship("Item", lazy="dynamic")  # Returns query object

# Order relationship results
items = relationship("Item", order_by="Item.name")

# Join conditions
items = relationship("Item", primaryjoin="and_(Parent.id==Item.parent_id, Item.active==True)")
```

## Creating Tables

```python
# Create all tables defined by Base subclasses
Base.metadata.create_all(engine)

# Create specific tables
Base.metadata.create_all(engine, tables=[User.__table__, Profile.__table__])

# Drop all tables
Base.metadata.drop_all(engine)
```

## CRUD Operations

### Create (Insert)

```python
# Create a single instance
user = User(name="John Doe", email="john@example.com", age=30)
session.add(user)
session.commit()

# Create multiple instances
users = [
    User(name="Jane Smith", email="jane@example.com", age=25),
    User(name="Bob Johnson", email="bob@example.com", age=35)
]
session.add_all(users)
session.commit()

# Get the ID after commit
new_user = User(name="Alice Brown", email="alice@example.com")
session.add(new_user)
session.commit()
print(f"New user ID: {new_user.id}")

# Bulk insert with Core (faster for many records)
from sqlalchemy import insert
stmt = insert(User.__table__).values([
    {"name": "User1", "email": "user1@example.com"},
    {"name": "User2", "email": "user2@example.com"}
])
engine.execute(stmt)
```

### Read (Query)

```python
# Get by primary key
user = session.get(User, 1)  # SQLAlchemy 2.0
# user = session.query(User).get(1)  # SQLAlchemy 1.x

# Query all
all_users = session.query(User).all()

# Filter with conditions
from sqlalchemy import and_, or_, not_

# Basic filters
users = session.query(User).filter(User.age > 25).all()
users = session.query(User).filter(User.name == "John Doe").first()
users = session.query(User).filter(User.name.like("%John%")).all()
users = session.query(User).filter(User.age.between(20, 30)).all()
users = session.query(User).filter(User.id.in_([1, 2, 3])).all()

# Multiple conditions
users = session.query(User).filter(
    and_(
        User.age > 25,
        User.name.like("%John%")
    )
).all()

users = session.query(User).filter(
    or_(
        User.age < 20,
        User.age > 30
    )
).all()

# Order results
users = session.query(User).order_by(User.age).all()  # Ascending
users = session.query(User).order_by(User.age.desc()).all()  # Descending

# Limit and offset
users = session.query(User).limit(10).all()
users = session.query(User).offset(10).limit(10).all()

# Count
count = session.query(User).filter(User.age > 25).count()

# Joins
employees = session.query(Employee, Department).join(Department).all()

# Left outer join
employees = session.query(Employee, Department).outerjoin(Department).all()

# Group by and aggregates
from sqlalchemy import func
result = session.query(
    Department.name,
    func.count(Employee.id).label('employee_count')
).join(Employee).group_by(Department.name).all()
```

### Update

```python
# Update a single instance
user = session.query(User).filter(User.id == 1).first()
user.name = "Updated Name"
session.commit()

# Bulk update
session.query(User).filter(User.age < 25).update({"status": "junior"})
session.commit()

# Update with expression
from sqlalchemy import update
stmt = update(User).where(User.id == 1).values(name="Updated Name")
session.execute(stmt)
session.commit()

# Update with expressions
from sqlalchemy import update, text
stmt = update(User).where(User.id == 1).values(
    login_count=User.login_count + 1,
    last_login=func.now()
)
session.execute(stmt)
session.commit()
```

### Delete

```python
# Delete a single instance
user = session.query(User).filter(User.id == 1).first()
session.delete(user)
session.commit()

# Bulk delete
session.query(User).filter(User.age < 25).delete()
session.commit()

# Delete with Core expression
from sqlalchemy import delete
stmt = delete(User).where(User.id == 1)
session.execute(stmt)
session.commit()
```

## Transactions

```python
# Explicit transaction
try:
    user1 = User(name="Transaction User 1")
    user2 = User(name="Transaction User 2")
    session.add(user1)
    session.add(user2)
    session.commit()
except Exception as e:
    session.rollback()
    print(f"Error: {e}")
finally:
    session.close()

# Using context manager (SQLAlchemy 1.4+)
from sqlalchemy.orm import Session

with Session(engine) as session:
    try:
        user = User(name="Context Manager User")
        session.add(user)
        session.commit()
    except:
        session.rollback()
        raise
```

## Alembic for Migrations

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init migrations

# Create a migration
alembic revision --autogenerate -m "Create users table"

# Run migrations
alembic upgrade head

# Downgrade
alembic downgrade -1  # Downgrade one revision
alembic downgrade base  # Downgrade all the way

# Get current revision
alembic current
```

## Using SQLAlchemy 2.0 Style

```python
# Import new syntax components
from sqlalchemy import select, insert, update, delete

# Select
stmt = select(User).where(User.name == "John").order_by(User.id)
result = session.execute(stmt)
for user in result.scalars():
    print(user.name)

# Insert
stmt = insert(User).values(name="John", email="john@example.com")
result = session.execute(stmt)
print(f"Inserted ID: {result.inserted_primary_key[0]}")

# Update
stmt = update(User).where(User.id == 1).values(name="Updated")
session.execute(stmt)

# Delete
stmt = delete(User).where(User.id == 1)
session.execute(stmt)

# Commit changes
session.commit()
```
