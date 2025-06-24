# GraphQL API with PostgreSQL, MongoDB, and Redis
# Requirements: pip install graphene flask psycopg2-binary pymongo redis

from flask import Flask, request, jsonify
import graphene
import psycopg2
from psycopg2.extras import RealDictCursor
import pymongo
import redis
import json
from datetime import datetime

# Database connections
def get_postgres_connection():
    return psycopg2.connect(
        host="localhost",
        database="myapp",
        user="username",
        password="password",
        cursor_factory=RealDictCursor
    )

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["myapp"]
posts_collection = mongo_db["posts"]

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# GraphQL Types
class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()
    posts = graphene.List(lambda: Post)
    view_count = graphene.Int()

class Post(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    content = graphene.String()
    user_id = graphene.ID()
    created_at = graphene.String()

class Comment(graphene.ObjectType):
    id = graphene.ID()
    content = graphene.String()
    post_id = graphene.ID()
    created_at = graphene.String()

# Resolvers
def resolve_user_posts(user_id):
    """Fetch posts from MongoDB"""
    posts = posts_collection.find({"user_id": str(user_id)})
    return [
        Post(
            id=str(post["_id"]),
            title=post["title"],
            content=post["content"],
            user_id=post["user_id"],
            created_at=post["created_at"].isoformat() if isinstance(post["created_at"], datetime) else post["created_at"]
        )
        for post in posts
    ]

def resolve_user_view_count(user_id):
    """Get view count from Redis cache"""
    count = redis_client.get(f"user:{user_id}:views")
    return int(count) if count else 0

def increment_user_views(user_id):
    """Increment user view count in Redis"""
    redis_client.incr(f"user:{user_id}:views")

# Query Class
class Query(graphene.ObjectType):
    user = graphene.Field(User, id=graphene.ID(required=True))
    users = graphene.List(User)
    post = graphene.Field(Post, id=graphene.ID(required=True))
    posts = graphene.List(Post)

    def resolve_user(self, info, id):
        """Fetch user from PostgreSQL"""
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return None
            
            # Increment view count when user is accessed
            increment_user_views(id)
            
            return User(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                posts=resolve_user_posts(id),
                view_count=resolve_user_view_count(id)
            )
        finally:
            cursor.close()
            conn.close()

    def resolve_users(self, info):
        """Fetch all users from PostgreSQL"""
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users ORDER BY name")
            users_data = cursor.fetchall()
            
            return [
                User(
                    id=user['id'],
                    name=user['name'],
                    email=user['email'],
                    posts=resolve_user_posts(user['id']),
                    view_count=resolve_user_view_count(user['id'])
                )
                for user in users_data
            ]
        finally:
            cursor.close()
            conn.close()

    def resolve_post(self, info, id):
        """Fetch single post from MongoDB"""
        from bson import ObjectId
        
        post = posts_collection.find_one({"_id": ObjectId(id)})
        if not post:
            return None
            
        return Post(
            id=str(post["_id"]),
            title=post["title"],
            content=post["content"],
            user_id=post["user_id"],
            created_at=post["created_at"].isoformat() if isinstance(post["created_at"], datetime) else post["created_at"]
        )

    def resolve_posts(self, info):
        """Fetch all posts from MongoDB"""
        posts = posts_collection.find().sort("created_at", -1)
        return [
            Post(
                id=str(post["_id"]),
                title=post["title"],
                content=post["content"],
                user_id=post["user_id"],
                created_at=post["created_at"].isoformat() if isinstance(post["created_at"], datetime) else post["created_at"]
            )
            for post in posts
        ]

# Mutations
class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(User)

    def mutate(self, info, name, email):
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING *",
                (name, email)
            )
            user_data = cursor.fetchone()
            conn.commit()
            
            # Initialize view count in Redis
            redis_client.set(f"user:{user_data['id']}:views", 0)
            
            return CreateUser(user=User(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                posts=[],
                view_count=0
            ))
        finally:
            cursor.close()
            conn.close()

class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        user_id = graphene.ID(required=True)

    post = graphene.Field(Post)

    def mutate(self, info, title, content, user_id):
        post_doc = {
            "title": title,
            "content": content,
            "user_id": str(user_id),
            "created_at": datetime.utcnow()
        }
        
        result = posts_collection.insert_one(post_doc)
        
        return CreatePost(post=Post(
            id=str(result.inserted_id),
            title=title,
            content=content,
            user_id=user_id,
            created_at=post_doc["created_at"].isoformat()
        ))

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_post = CreatePost.Field()

# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# Flask App
app = Flask(__name__)

@app.route('/graphql', methods=['POST'])
def graphql():
    data = request.get_json()
    
    result = schema.execute(
        data.get('query'),
        variables=data.get('variables'),
        context={'request': request}
    )
    
    return jsonify({
        'data': result.data,
        'errors': [str(error) for error in result.errors] if result.errors else None
    })

@app.route('/graphiql')
def graphiql():
    """Simple GraphiQL interface for testing"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>GraphiQL</title>
        <link href="https://unpkg.com/graphiql@1.4.7/graphiql.min.css" rel="stylesheet" />
    </head>
    <body style="margin: 0;">
        <div id="graphiql" style="height: 100vh;"></div>
        <script crossorigin src="https://unpkg.com/react@17/umd/react.development.js"></script>
        <script crossorigin src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
        <script crossorigin src="https://unpkg.com/graphiql@1.4.7/graphiql.min.js"></script>
        <script>
            ReactDOM.render(
                React.createElement(GraphiQL, {
                    fetcher: function(params) {
                        return fetch('/graphql', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(params),
                        }).then(response => response.json());
                    }
                }),
                document.getElementById('graphiql')
            );
        </script>
    </body>
    </html>
    '''

# Database setup scripts (run these separately)
def setup_postgres():
    """Create PostgreSQL table"""
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    # Uncomment to setup database schema
    # setup_postgres()
    
    app.run(debug=True)

# Example GraphQL Queries:
"""
# Query user with posts (data from PostgreSQL + MongoDB + Redis)
query {
  user(id: "1") {
    name
    email
    viewCount
    posts {
      title
      content
      createdAt
    }
  }
}

# Create new user (stored in PostgreSQL)
mutation {
  createUser(name: "John Doe", email: "john@example.com") {
    user {
      id
      name
      email
      viewCount
    }
  }
}

# Create new post (stored in MongoDB)
mutation {
  createPost(title: "My First Post", content: "Hello World!", userId: "1") {
    post {
      id
      title
      content
      userId
      createdAt
    }
  }
}

# Query all users with their post counts
query {
  users {
    name
    email
    viewCount
    posts {
      title
    }
  }
}
"""
