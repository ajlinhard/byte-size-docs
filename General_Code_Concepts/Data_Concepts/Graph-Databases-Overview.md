# Graph Database Guide
Graph databases like Neptune work fundamentally differently from relational databases by storing data as interconnected nodes and relationships rather than tables with rows and columns.

### [Key Vocabulary and Concepts](#key-vocabulary-and-concepts)
- [Graph Database Terms](#graph-database-terms)
- [Query Languages](#query-languages)

### [How Graph Databases Differ from Relational Databases](#how-graph-databases-differ-from-relational-databases)
- [Relational Database Structure](#relational-database-structure)
- [Graph Database Structure](#graph-database-structure)

## [Neptune-Specific Code Examples](#neptune-specific-code-examples)
- [NeptuneGraphDB Class](#neptunegraphdb-class)
  - [Connection Management](#connection-management)
  - [Adding Data](#adding-data)
  - [Querying/Selecting Data](#queryingselecting-data)
  - [Joining/Traversing Relationships](#joiningtraversing-relationships)
  - [Updating Data](#updating-data)
  - [Deleting Data](#deleting-data)
- [Example Usage](#example-usage)

### [SQL vs Gremlin Comparison](#sql-vs-gremlin-comparison)
- [Basic Operations](#basic-operations)
  - [Select All Records](#select-all-records)
  - [Select with Where Condition](#select-with-where-condition)
  - [Insert Data](#insert-data)
  - [Update Data](#update-data)
  - [Delete Data](#delete-data)
- [Advanced Operations](#advanced-operations)
  - [Join Tables vs Traverse Relationships](#join-tables-vs-traverse-relationships)
  - [Complex Joins - Find Colleagues](#complex-joins---find-colleagues)
  - [Aggregate Functions](#aggregate-functions)
  - [Subqueries vs Graph Patterns](#subqueries-vs-graph-patterns)
  - [Recursive/Multi-Hop Queries](#recursivemulti-hop-queries)

### [Key Advantages of Graph Databases](#key-advantages-of-graph-databases)
- [Performance Benefits](#performance-benefits)
- [Flexibility Benefits](#flexibility-benefits)
- [Query Expressiveness](#query-expressiveness)
- [When to Use Graph Databases](#when-to-use-graph-databases)

## Key Vocabulary and Concepts

**Graph Database Terms:**
- **Node (Vertex)**: An entity or object in the graph, like a person, product, or location
- **Edge (Relationship)**: A connection between two nodes that represents how they're related
- **Property**: Key-value pairs that store attributes on both nodes and edges
- **Label**: Categories or types that classify nodes (e.g., "Person", "Product")
- **Graph**: The complete collection of nodes and edges forming a network structure

**Query Languages:**
- **Gremlin**: A graph traversal language used by Neptune and other graph databases
- **SPARQL**: Query language for RDF (Resource Description Framework) data
- **Cypher**: Neo4j's declarative graph query language (not natively supported by Neptune)

## How Graph Databases Differ from Relational Databases

**Relational Database Structure:**
- Data stored in tables with predefined schemas
- Relationships expressed through foreign keys
- Joins required to connect related data across tables
- Performance degrades with complex multi-table joins

**Graph Database Structure:**
- Data stored as nodes connected by edges
- Relationships are first-class citizens with their own properties
- No joins needed - traverse relationships directly
- Performance remains consistent regardless of relationship complexity

## Neptune-Specific Code Examples
```python
import boto3
from gremlin_python.driver import client
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.process.traversal import T, P, Operator
import json

# Configuration for Neptune connection
NEPTUNE_ENDPOINT = "your-neptune-cluster.cluster-xxxxx.us-east-1.neptune.amazonaws.com"
NEPTUNE_PORT = 8182

class NeptuneGraphDB:
    def __init__(self, endpoint, port):
        self.endpoint = endpoint
        self.port = port
        self.connection = None
        self.g = None
        
    def connect(self):
        """Establish connection to Neptune"""
        try:
            # Create WebSocket connection to Neptune
            self.connection = DriverRemoteConnection(
                f'wss://{self.endpoint}:{self.port}/gremlin', 'g'
            )
            # Create graph traversal source
            self.g = traversal().withRemote(self.connection)
            print("Connected to Neptune successfully")
        except Exception as e:
            print(f"Connection failed: {e}")
    
    def disconnect(self):
        """Close Neptune connection"""
        if self.connection:
            self.connection.close()
            print("Disconnected from Neptune")

    # ============ ADDING DATA ============
    
    def add_person_node(self, person_id, name, age, city):
        """Add a person node with properties"""
        try:
            result = (self.g.addV('Person')
                     .property(T.id, person_id)
                     .property('name', name)
                     .property('age', age)
                     .property('city', city)
                     .next())
            print(f"Added person: {name}")
            return result
        except Exception as e:
            print(f"Error adding person: {e}")
    
    def add_company_node(self, company_id, name, industry, founded_year):
        """Add a company node with properties"""
        try:
            result = (self.g.addV('Company')
                     .property(T.id, company_id)
                     .property('name', name)
                     .property('industry', industry)
                     .property('founded_year', founded_year)
                     .next())
            print(f"Added company: {name}")
            return result
        except Exception as e:
            print(f"Error adding company: {e}")
    
    def add_employment_relationship(self, person_id, company_id, role, start_date, salary):
        """Add WORKS_FOR relationship between person and company"""
        try:
            result = (self.g.V(person_id)
                     .addE('WORKS_FOR')
                     .to(self.g.V(company_id))
                     .property('role', role)
                     .property('start_date', start_date)
                     .property('salary', salary)
                     .next())
            print(f"Added employment relationship")
            return result
        except Exception as e:
            print(f"Error adding relationship: {e}")
    
    def add_friendship_relationship(self, person1_id, person2_id, since_year):
        """Add bidirectional FRIENDS_WITH relationship"""
        try:
            # Add edge from person1 to person2
            self.g.V(person1_id).addE('FRIENDS_WITH').to(self.g.V(person2_id)).property('since', since_year).next()
            # Add edge from person2 to person1 (bidirectional)
            self.g.V(person2_id).addE('FRIENDS_WITH').to(self.g.V(person1_id)).property('since', since_year).next()
            print(f"Added friendship relationship")
        except Exception as e:
            print(f"Error adding friendship: {e}")

    # ============ QUERYING/SELECTING DATA ============
    
    def get_all_people(self):
        """Select all person nodes"""
        try:
            people = (self.g.V()
                     .hasLabel('Person')
                     .valueMap(True)  # True includes id and label
                     .toList())
            print("All people in database:")
            for person in people:
                print(f"  {person}")
            return people
        except Exception as e:
            print(f"Error querying people: {e}")
    
    def find_person_by_name(self, name):
        """Find specific person by name"""
        try:
            person = (self.g.V()
                     .hasLabel('Person')
                     .has('name', name)
                     .valueMap(True)
                     .toList())
            if person:
                print(f"Found person: {person[0]}")
                return person[0]
            else:
                print(f"Person {name} not found")
                return None
        except Exception as e:
            print(f"Error finding person: {e}")
    
    def get_people_by_age_range(self, min_age, max_age):
        """Select people within age range"""
        try:
            people = (self.g.V()
                     .hasLabel('Person')
                     .has('age', P.between(min_age, max_age))
                     .valueMap('name', 'age', 'city')
                     .toList())
            print(f"People aged {min_age}-{max_age}:")
            for person in people:
                print(f"  {person}")
            return people
        except Exception as e:
            print(f"Error querying by age: {e}")

    # ============ JOINING/TRAVERSING RELATIONSHIPS ============
    
    def get_person_employment_info(self, person_name):
        """Get person and their employment details (equivalent to SQL JOIN)"""
        try:
            result = (self.g.V()
                     .hasLabel('Person')
                     .has('name', person_name)
                     .as_('person')
                     .outE('WORKS_FOR')
                     .as_('job')
                     .inV()
                     .as_('company')
                     .select('person', 'job', 'company')
                     .by(__.valueMap('name', 'age', 'city'))
                     .by(__.valueMap('role', 'salary', 'start_date'))
                     .by(__.valueMap('name', 'industry'))
                     .toList())
            
            print(f"Employment info for {person_name}:")
            for employment in result:
                person = employment['person']
                job = employment['job'] 
                company = employment['company']
                print(f"  Person: {person['name'][0]}, Age: {person['age'][0]}")
                print(f"  Role: {job['role'][0]}, Salary: ${job['salary'][0]:,}")
                print(f"  Company: {company['name'][0]}, Industry: {company['industry'][0]}")
            return result
        except Exception as e:
            print(f"Error getting employment info: {e}")
    
    def find_colleagues(self, person_name):
        """Find people who work at the same company (2-hop traversal)"""
        try:
            colleagues = (self.g.V()
                         .hasLabel('Person')
                         .has('name', person_name)
                         .out('WORKS_FOR')  # Go to company
                         .in_('WORKS_FOR')  # Find all employees
                         .has('name', P.neq(person_name))  # Exclude original person
                         .valueMap('name', 'age')
                         .toList())
            
            print(f"Colleagues of {person_name}:")
            for colleague in colleagues:
                print(f"  {colleague['name'][0]}, Age: {colleague['age'][0]}")
            return colleagues
        except Exception as e:
            print(f"Error finding colleagues: {e}")
    
    def find_friends_of_friends(self, person_name):
        """Find friends of friends (2-hop friendship traversal)"""
        try:
            friends_of_friends = (self.g.V()
                                 .hasLabel('Person')
                                 .has('name', person_name)
                                 .out('FRIENDS_WITH')  # Get friends
                                 .out('FRIENDS_WITH')  # Get friends of friends
                                 .has('name', P.neq(person_name))  # Exclude original person
                                 .dedup()  # Remove duplicates
                                 .valueMap('name', 'city')
                                 .toList())
            
            print(f"Friends of friends for {person_name}:")
            for friend in friends_of_friends:
                print(f"  {friend['name'][0]} from {friend['city'][0]}")
            return friends_of_friends
        except Exception as e:
            print(f"Error finding friends of friends: {e}")
    
    def get_company_employee_count(self):
        """Aggregate query: Count employees per company"""
        try:
            company_counts = (self.g.V()
                             .hasLabel('Company')
                             .as_('company')
                             .in_('WORKS_FOR')
                             .count()
                             .as_('employee_count')
                             .select('company', 'employee_count')
                             .by(__.valueMap('name'))
                             .by()
                             .toList())
            
            print("Employee count by company:")
            for company_data in company_counts:
                company_name = company_data['company']['name'][0]
                count = company_data['employee_count']
                print(f"  {company_name}: {count} employees")
            return company_counts
        except Exception as e:
            print(f"Error getting employee counts: {e}")

    # ============ UPDATING DATA ============
    
    def update_person_age(self, person_name, new_age):
        """Update person's age property"""
        try:
            result = (self.g.V()
                     .hasLabel('Person')
                     .has('name', person_name)
                     .property('age', new_age)
                     .valueMap('name', 'age')
                     .next())
            print(f"Updated {person_name}'s age to {new_age}")
            return result
        except Exception as e:
            print(f"Error updating age: {e}")
    
    def update_salary(self, person_name, new_salary):
        """Update employment relationship salary"""
        try:
            result = (self.g.V()
                     .hasLabel('Person')
                     .has('name', person_name)
                     .outE('WORKS_FOR')
                     .property('salary', new_salary)
                     .valueMap()
                     .next())
            print(f"Updated {person_name}'s salary to ${new_salary:,}")
            return result
        except Exception as e:
            print(f"Error updating salary: {e}")

    # ============ DELETING DATA ============
    
    def delete_person(self, person_name):
        """Delete person node and all associated edges"""
        try:
            # First, delete all edges connected to this person
            self.g.V().hasLabel('Person').has('name', person_name).bothE().drop().iterate()
            # Then delete the person node
            result = self.g.V().hasLabel('Person').has('name', person_name).drop().iterate()
            print(f"Deleted person: {person_name}")
            return result
        except Exception as e:
            print(f"Error deleting person: {e}")
    
    def delete_employment_relationship(self, person_name, company_name):
        """Delete specific employment relationship"""
        try:
            result = (self.g.V()
                     .hasLabel('Person')
                     .has('name', person_name)
                     .outE('WORKS_FOR')
                     .where(__.inV().has('name', company_name))
                     .drop()
                     .iterate())
            print(f"Deleted employment relationship between {person_name} and {company_name}")
            return result
        except Exception as e:
            print(f"Error deleting relationship: {e}")
    
    def delete_all_friendships(self, person_name):
        """Delete all friendship relationships for a person"""
        try:
            result = (self.g.V()
                     .hasLabel('Person')
                     .has('name', person_name)
                     .bothE('FRIENDS_WITH')
                     .drop()
                     .iterate())
            print(f"Deleted all friendships for {person_name}")
            return result
        except Exception as e:
            print(f"Error deleting friendships: {e}")

# ============ EXAMPLE USAGE ============

def main():
    # Initialize Neptune connection
    db = NeptuneGraphDB(NEPTUNE_ENDPOINT, NEPTUNE_PORT)
    db.connect()
    
    try:
        # Add sample data
        print("=== ADDING DATA ===")
        db.add_person_node('person1', 'Alice Johnson', 28, 'Seattle')
        db.add_person_node('person2', 'Bob Smith', 32, 'Portland')
        db.add_person_node('person3', 'Carol Davis', 29, 'Seattle')
        
        db.add_company_node('company1', 'TechCorp', 'Technology', 2015)
        db.add_company_node('company2', 'DataSoft', 'Software', 2018)
        
        db.add_employment_relationship('person1', 'company1', 'Software Engineer', '2022-01-15', 95000)
        db.add_employment_relationship('person2', 'company1', 'Product Manager', '2021-06-01', 110000)
        db.add_employment_relationship('person3', 'company2', 'Data Scientist', '2023-03-01', 105000)
        
        db.add_friendship_relationship('person1', 'person2', 2020)
        db.add_friendship_relationship('person2', 'person3', 2021)
        
        # Query data
        print("\n=== QUERYING DATA ===")
        db.get_all_people()
        db.find_person_by_name('Alice Johnson')
        db.get_people_by_age_range(25, 30)
        
        # Join/traverse relationships
        print("\n=== RELATIONSHIP TRAVERSALS ===")
        db.get_person_employment_info('Alice Johnson')
        db.find_colleagues('Alice Johnson')
        db.find_friends_of_friends('Alice Johnson')
        db.get_company_employee_count()
        
        # Update data
        print("\n=== UPDATING DATA ===")
        db.update_person_age('Alice Johnson', 29)
        db.update_salary('Bob Smith', 115000)
        
        # Delete data
        print("\n=== DELETING DATA ===")
        db.delete_employment_relationship('Carol Davis', 'DataSoft')
        db.delete_all_friendships('Bob Smith')
        
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()
```

---
# SQL vs Gremlin
Here are practical examples using Python with the Gremlin client:## SQL vs Gremlin Comparison
```python
-- ============ SQL vs GREMLIN COMPARISON ============

-- 1. SELECT ALL RECORDS
-- SQL:
SELECT * FROM people;

-- Gremlin equivalent:
g.V().hasLabel('Person').valueMap(true).toList()

-- 2. SELECT WITH WHERE CONDITION
-- SQL:
SELECT name, age FROM people WHERE age > 25;

-- Gremlin equivalent:
g.V().hasLabel('Person').has('age', P.gt(25)).valueMap('name', 'age').toList()

-- 3. INSERT DATA
-- SQL:
INSERT INTO people (id, name, age, city) VALUES (1, 'Alice', 28, 'Seattle');

-- Gremlin equivalent:
g.addV('Person').property(T.id, 1).property('name', 'Alice').property('age', 28).property('city', 'Seattle').next()

-- 4. UPDATE DATA
-- SQL:
UPDATE people SET age = 29 WHERE name = 'Alice';

-- Gremlin equivalent:
g.V().hasLabel('Person').has('name', 'Alice').property('age', 29).next()

-- 5. DELETE DATA
-- SQL:
DELETE FROM people WHERE name = 'Alice';

-- Gremlin equivalent:
g.V().hasLabel('Person').has('name', 'Alice').drop().iterate()

-- 6. JOIN TABLES (SQL) vs TRAVERSE RELATIONSHIPS (Gremlin)
-- SQL JOIN:
SELECT p.name, p.age, c.name as company_name, e.role, e.salary
FROM people p
JOIN employment e ON p.id = e.person_id
JOIN companies c ON e.company_id = c.id
WHERE p.name = 'Alice';

-- Gremlin traversal (no joins needed):
g.V().hasLabel('Person').has('name', 'Alice')
  .as_('person')
  .outE('WORKS_FOR').as_('job')
  .inV().as_('company')
  .select('person', 'job', 'company')
  .by(__.valueMap('name', 'age'))
  .by(__.valueMap('role', 'salary'))
  .by(__.valueMap('name'))
  .toList()

-- 7. COMPLEX JOIN - Find colleagues (people who work at same company)
-- SQL:
SELECT DISTINCT p2.name, p2.age
FROM people p1
JOIN employment e1 ON p1.id = e1.person_id
JOIN employment e2 ON e1.company_id = e2.company_id
JOIN people p2 ON e2.person_id = p2.id
WHERE p1.name = 'Alice' AND p2.name != 'Alice';

-- Gremlin (much simpler):
g.V().hasLabel('Person').has('name', 'Alice')
  .out('WORKS_FOR')
  .in_('WORKS_FOR')
  .has('name', P.neq('Alice'))
  .valueMap('name', 'age')
  .toList()

-- 8. AGGREGATE FUNCTIONS
-- SQL:
SELECT c.name, COUNT(e.person_id) as employee_count
FROM companies c
LEFT JOIN employment e ON c.id = e.company_id
GROUP BY c.id, c.name;

-- Gremlin:
g.V().hasLabel('Company')
  .as_('company')
  .in_('WORKS_FOR').count().as_('count')
  .select('company', 'count')
  .by(__.valueMap('name'))
  .by()
  .toList()

-- 9. SUBQUERIES vs GRAPH PATTERNS
-- SQL - Find people who have friends in Seattle:
SELECT DISTINCT p1.name
FROM people p1
WHERE p1.id IN (
    SELECT f.person1_id 
    FROM friendships f
    JOIN people p2 ON f.person2_id = p2.id
    WHERE p2.city = 'Seattle'
    UNION
    SELECT f.person2_id 
    FROM friendships f
    JOIN people p2 ON f.person1_id = p2.id
    WHERE p2.city = 'Seattle'
);

-- Gremlin (natural graph traversal):
g.V().hasLabel('Person')
  .where(__.out('FRIENDS_WITH').has('city', 'Seattle'))
  .valueMap('name')
  .toList()

-- 10. RECURSIVE/MULTI-HOP QUERIES
-- SQL - Find friends of friends (requires complex recursive CTE):
WITH RECURSIVE friend_network AS (
    SELECT person1_id as start_person, person2_id as friend, 1 as level
    FROM friendships WHERE person1_id = 1
    UNION
    SELECT person2_id as start_person, person1_id as friend, 1 as level  
    FROM friendships WHERE person2_id = 1
    UNION
    SELECT fn.start_person, f.person2_id, fn.level + 1
    FROM friend_network fn
    JOIN friendships f ON fn.friend = f.person1_id
    WHERE fn.level < 2
    UNION
    SELECT fn.start_person, f.person1_id, fn.level + 1
    FROM friend_network fn  
    JOIN friendships f ON fn.friend = f.person2_id
    WHERE fn.level < 2
)
SELECT DISTINCT p.name
FROM friend_network fn
JOIN people p ON fn.friend = p.id
WHERE fn.level = 2 AND fn.start_person = 1;

-- Gremlin (simple and intuitive):
g.V().hasLabel('Person').has('name', 'Alice')
  .out('FRIENDS_WITH')
  .out('FRIENDS_WITH')
  .has('name', P.neq('Alice'))
  .dedup()
  .valueMap('name')
  .toList()

-- KEY ADVANTAGES OF GRAPH DATABASES:

-- 1. NO COMPLEX JOINS: Relationships are first-class, traverse naturally
-- 2. PERFORMANCE: Relationship traversals are O(1), not dependent on table size
-- 3. FLEXIBILITY: Easy to add new relationship types without schema changes
-- 4. INTUITIVE: Queries mirror how you think about connected data
-- 5. RECURSIVE QUERIES: Multi-hop traversals are simple and efficient

-- WHEN TO USE GRAPH DATABASES:
-- - Social networks and recommendations
-- - Fraud detection (finding suspicious patterns)
-- - Network and IT operations (dependency mapping)
-- - Knowledge graphs and semantic data
-- - Supply chain and logistics
-- - Identity and access management
-- - Real-time recommendation engines
```
Here's how common database operations translate between SQL and Gremlin:## Key Advantages of Graph Databases

**Performance Benefits:**
- **Constant Time Traversals**: Following relationships is O(1) regardless of database size
- **No Join Overhead**: Relationships are pre-computed and stored as first-class entities
- **Local Queries**: Most graph queries only touch a small portion of the database

**Flexibility Benefits:**
- **Schema-Free**: Add new node types and relationships without migrations
- **Evolving Relationships**: Easily add properties to edges as requirements change
- **Multiple Relationship Types**: One node can have many different types of connections

**Query Expressiveness:**
- **Natural Patterns**: Queries mirror how humans think about connected data
- **Multi-Hop Traversals**: Complex recursive queries become simple traversals
- **Pattern Matching**: Find complex patterns across multiple relationships

Graph databases excel when your data has rich interconnections and you need to perform complex relationship queries efficiently. They're particularly powerful for social networks, recommendation engines, fraud detection, and any domain where relationships between entities are as important as the entities themselves.
