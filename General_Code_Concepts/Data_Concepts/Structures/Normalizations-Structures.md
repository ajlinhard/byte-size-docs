# Normalization Structures
# Database Normalization Forms

Database normalization is a process of organizing data to reduce redundancy and improve data integrity. Here are the main normal forms with detailed examples:

## **First Normal Form (1NF)**

**Requirements:**
- Each column must contain only atomic (indivisible) values
- Each column must contain values of a single type
- Each row must be unique (usually enforced by a primary key)
- No repeating groups or arrays

**Example - Violation of 1NF:**

| StudentID | Name | PhoneNumbers |
|-----------|------|--------------|
| 1 | John Smith | 555-1234, 555-5678 |
| 2 | Jane Doe | 555-9999 |

**Corrected to 1NF:**

| StudentID | Name | PhoneNumber |
|-----------|------|-------------|
| 1 | John Smith | 555-1234 |
| 1 | John Smith | 555-5678 |
| 2 | Jane Doe | 555-9999 |

---

## **Second Normal Form (2NF)**

**Requirements:**
- Must be in 1NF
- All non-key attributes must be fully functionally dependent on the **entire** primary key
- Eliminates partial dependencies (relevant when you have a composite primary key)

**Example - Violation of 2NF:**

Table with composite key (StudentID, CourseID):

| StudentID | CourseID | StudentName | CourseName | Grade |
|-----------|----------|-------------|------------|-------|
| 1 | CS101 | John Smith | Intro to CS | A |
| 1 | MATH201 | John Smith | Calculus | B |
| 2 | CS101 | Jane Doe | Intro to CS | A |

**Problem**: StudentName depends only on StudentID (partial dependency), and CourseName depends only on CourseID (partial dependency).

**Corrected to 2NF:**

**Students Table:**
| StudentID | StudentName |
|-----------|-------------|
| 1 | John Smith |
| 2 | Jane Doe |

**Courses Table:**
| CourseID | CourseName |
|----------|------------|
| CS101 | Intro to CS |
| MATH201 | Calculus |

**Enrollments Table:**
| StudentID | CourseID | Grade |
|-----------|----------|-------|
| 1 | CS101 | A |
| 1 | MATH201 | B |
| 2 | CS101 | A |

---

## **Third Normal Form (3NF)**

**Requirements:**
- Must be in 2NF
- No transitive dependencies (non-key attributes must not depend on other non-key attributes)
- Every non-key attribute must depend directly on the primary key

**Example - Violation of 3NF:**

| StudentID | StudentName | ZipCode | City | State |
|-----------|-------------|---------|------|-------|
| 1 | John Smith | 10001 | New York | NY |
| 2 | Jane Doe | 90210 | Beverly Hills | CA |
| 3 | Bob Jones | 10001 | New York | NY |

**Problem**: City and State depend on ZipCode, not directly on StudentID (transitive dependency: StudentID → ZipCode → City, State).

**Corrected to 3NF:**

**Students Table:**
| StudentID | StudentName | ZipCode |
|-----------|-------------|---------|
| 1 | John Smith | 10001 |
| 2 | Jane Doe | 90210 |
| 3 | Bob Jones | 10001 |

**ZipCodes Table:**
| ZipCode | City | State |
|---------|------|-------|
| 10001 | New York | NY |
| 90210 | Beverly Hills | CA |

---

## **Boyce-Codd Normal Form (BCNF)**

**Requirements:**
- A stricter version of 3NF
- For every functional dependency X → Y, X must be a superkey (a candidate key)
- Handles anomalies where a table is in 3NF but still has update anomalies

**Example - Violation of BCNF:**

| StudentID | Course | Instructor |
|-----------|--------|------------|
| 1 | Database | Dr. Smith |
| 2 | Database | Dr. Smith |
| 3 | Algorithms | Dr. Jones |
| 4 | Database | Dr. Brown |

**Assumptions**: 
- Each instructor teaches only one course
- A course can have multiple instructors
- Instructor → Course (but Instructor is not a candidate key)

**Problem**: Instructor determines Course, but Instructor is not a superkey.

**Corrected to BCNF:**

**Student-Instructor Table:**
| StudentID | Instructor |
|-----------|------------|
| 1 | Dr. Smith |
| 2 | Dr. Smith |
| 3 | Dr. Jones |
| 4 | Dr. Brown |

**Instructor-Course Table:**
| Instructor | Course |
|------------|--------|
| Dr. Smith | Database |
| Dr. Jones | Algorithms |
| Dr. Brown | Database |

---

## **Fourth Normal Form (4NF)**

**Requirements:**
- Must be in BCNF
- No multi-valued dependencies (when one attribute independently determines multiple values of other attributes)

**Example - Violation of 4NF:**

| StudentID | Course | Hobby |
|-----------|--------|-------|
| 1 | Database | Tennis |
| 1 | Database | Reading |
| 1 | Algorithms | Tennis |
| 1 | Algorithms | Reading |

**Problem**: Courses and Hobbies are independent of each other but both depend on StudentID, creating redundancy.

**Corrected to 4NF:**

**Student-Course Table:**
| StudentID | Course |
|-----------|--------|
| 1 | Database |
| 1 | Algorithms |

**Student-Hobby Table:**
| StudentID | Hobby |
|-----------|-------|
| 1 | Tennis |
| 1 | Reading |

---

## **Fifth Normal Form (5NF)**

**Requirements:**
- Must be in 4NF
- No join dependencies (the table cannot be decomposed into smaller tables without losing information when joined back)
- Every join dependency must be implied by candidate keys

**Example - Violation of 5NF:**

| Supplier | Product | Customer |
|----------|---------|----------|
| SupplierA | Widget | CustomerX |
| SupplierA | Gadget | CustomerY |
| SupplierB | Widget | CustomerX |

**If these rules hold:**
- If a supplier supplies a product, and a customer orders that product, and the customer orders from that supplier, then the supplier supplies that product to that customer

**Corrected to 5NF:**

**Supplier-Product Table:**
| Supplier | Product |
|----------|---------|
| SupplierA | Widget |
| SupplierA | Gadget |
| SupplierB | Widget |

**Product-Customer Table:**
| Product | Customer |
|---------|----------|
| Widget | CustomerX |
| Gadget | CustomerY |

**Supplier-Customer Table:**
| Supplier | Customer |
|----------|----------|
| SupplierA | CustomerX |
| SupplierA | CustomerY |
| SupplierB | CustomerX |

---

## **Practical Considerations**

In practice, most databases aim for **3NF** as it provides an excellent balance between:
- Data integrity and consistency
- Query performance
- Ease of maintenance

Higher normal forms (BCNF, 4NF, 5NF) are used only when specific anomalies need to be addressed, as they can sometimes make queries more complex and potentially slower due to additional joins.
