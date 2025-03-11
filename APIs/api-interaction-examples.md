# API Interaction Examples

## 1. CURL Commands
```bash
# GET all books
curl http://localhost:5000/books

# GET a specific book by ID
curl http://localhost:5000/books/1

# POST (Create) a new book
curl -X POST http://localhost:5000/books \
     -H "Content-Type: application/json" \
     -d '{"title":"The Great Gatsby", "author":"F. Scott Fitzgerald", "isbn":"9780743273565"}'

# PUT (Update) an existing book
curl -X PUT http://localhost:5000/books/1 \
     -H "Content-Type: application/json" \
     -d '{"title":"Updated Title"}'

# DELETE a book
curl -X DELETE http://localhost:5000/books/1
```

## 2. Python Requests Example
```python
import requests

class BookAPIClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def get_all_books(self):
        """Retrieve all books"""
        response = requests.get(f'{self.base_url}/books')
        return response.json()

    def get_book(self, book_id):
        """Retrieve a specific book"""
        response = requests.get(f'{self.base_url}/books/{book_id}')
        return response.json()

    def create_book(self, book_data):
        """Create a new book"""
        response = requests.post(
            f'{self.base_url}/books', 
            json=book_data
        )
        return response.json()

    def update_book(self, book_id, book_data):
        """Update an existing book"""
        response = requests.put(
            f'{self.base_url}/books/{book_id}', 
            json=book_data
        )
        return response.json()

    def delete_book(self, book_id):
        """Delete a book"""
        response = requests.delete(f'{self.base_url}/books/{book_id}')
        return response.status_code == 204

# Example usage
def main():
    client = BookAPIClient()
    
    # Get all books
    print("All Books:", client.get_all_books())
    
    # Create a new book
    new_book = {
        "title": "Dune",
        "author": "Frank Herbert",
        "isbn": "9780441172719"
    }
    created_book = client.create_book(new_book)
    print("Created Book:", created_book)
    
    # Update the book
    updated_book = client.update_book(created_book['id'], {"title": "Dune: Updated"})
    print("Updated Book:", updated_book)
    
    # Delete the book
    client.delete_book(created_book['id'])

if __name__ == '__main__':
    main()
```

## 3. Java HttpClient Example
```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import com.google.gson.Gson;
import java.io.IOException;

public class BookAPIClient {
    private final String baseUrl;
    private final HttpClient httpClient;
    private final Gson gson;

    public BookAPIClient(String baseUrl) {
        this.baseUrl = baseUrl;
        this.httpClient = HttpClient.newHttpClient();
        this.gson = new Gson();
    }

    public String getAllBooks() throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books"))
            .GET()
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String getBook(int bookId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books/" + bookId))
            .GET()
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String createBook(Book book) throws IOException, InterruptedException {
        String jsonBook = gson.toJson(book);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonBook))
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String updateBook(int bookId, Book book) throws IOException, InterruptedException {
        String jsonBook = gson.toJson(book);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books/" + bookId))
            .header("Content-Type", "application/json")
            .PUT(HttpRequest.BodyPublishers.ofString(jsonBook))
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public boolean deleteBook(int bookId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books/" + bookId))
            .DELETE()
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.statusCode() == 204;
    }

    // Book model class
    public static class Book {
        private int id;
        private String title;
        private String author;
        private String isbn;

        // Constructors, getters, and setters
        public Book(String title, String author, String isbn) {
            this.title = title;
            this.author = author;
            this.isbn = isbn;
        }
    }

    // Example usage
    public static void main(String[] args) {
        try {
            BookAPIClient client = new BookAPIClient("http://localhost:5000");
            
            // Get all books
            String allBooks = client.getAllBooks();
            System.out.println("All Books: " + allBooks);
            
            // Create a new book
            Book newBook = new Book("Dune", "Frank Herbert", "9780441172719");
            String createdBook = client.createBook(newBook);
            System.out.println("Created Book: " + createdBook);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

## Dependencies
- **Python**: `requests` library
- **Java**: 
  - `java.net.http` (Java 11+)
  - `com.google.gson` for JSON parsing

## Key Considerations
1. Error handling
2. Authentication (if required)
3. SSL/TLS for secure connections
4. Proper exception management
5. Configurable base URL
```

Let me break down the key aspects of API interaction:

1. **CURL**
   - Command-line tool for making HTTP requests
   - Simple, quick for testing
   - Supports all HTTP methods (GET, POST, PUT, DELETE)

2. **Python**
   - Uses `requests` library
   - Object-oriented approach
   - Easy error handling
   - JSON parsing built-in

3. **Java**
   - Uses modern `HttpClient` (Java 11+)
   - Requires more boilerplate code
   - Uses Gson for JSON serialization/deserialization
   - Strong type checking

Each approach follows a similar pattern:
- Create a client
- Define methods for each API endpoint
- Handle HTTP requests and responses
- Parse JSON data

Recommendations:
- Add error handling
- Implement retry mechanisms
- Use environment variables for base URL
- Add logging
- Consider authentication tokens

Would you like me to elaborate on any specific aspect of API interaction or explain how to handle more complex scenarios?