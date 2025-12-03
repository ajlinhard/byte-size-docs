"""
Example 1: SQLAlchemy + Pydantic (Separate Models)
Traditional approach with clear separation of concerns
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, Session
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# ============================================================================
# SQLAlchemy Models (Database Layer)
# ============================================================================
Base = declarative_base()

class UserDB(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    posts = relationship("PostDB", back_populates="author", cascade="all, delete-orphan")


class PostDB(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    published = Column(Integer, default=0)  # SQLite doesn't have boolean
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    author = relationship("UserDB", back_populates="posts")


# ============================================================================
# Pydantic Models (API/Validation Layer)
# ============================================================================

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2


class UserWithPosts(UserResponse):
    posts: List['PostResponse'] = []


# Post Schemas
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = False


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    published: Optional[bool] = None


class PostResponse(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PostWithAuthor(PostResponse):
    author: UserResponse


# ============================================================================
# CRUD Operations
# ============================================================================

def hash_password(password: str) -> str:
    """Simulate password hashing"""
    return f"hashed_{password}"


def create_user(db: Session, user: UserCreate) -> UserResponse:
    """Create a new user"""
    db_user = UserDB(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Convert SQLAlchemy model to Pydantic
    return UserResponse.model_validate(db_user)


def get_user(db: Session, user_id: int) -> Optional[UserResponse]:
    """Get user by ID"""
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user:
        return UserResponse.model_validate(db_user)
    return None


def create_post(db: Session, post: PostCreate, author_id: int) -> PostResponse:
    """Create a new post"""
    db_post = PostDB(
        title=post.title,
        content=post.content,
        published=1 if post.published else 0,
        author_id=author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return PostResponse.model_validate(db_post)


def get_posts_by_user(db: Session, user_id: int) -> List[PostResponse]:
    """Get all posts by a user"""
    posts = db.query(PostDB).filter(PostDB.author_id == user_id).all()
    return [PostResponse.model_validate(post) for post in posts]


# ============================================================================
# Demo Usage
# ============================================================================

def main():
    # Setup database
    engine = create_engine('sqlite:///sqlalchemy_pydantic.db', echo=False)
    Base.metadata.create_all(engine)
    
    with Session(engine) as db:
        # Create user
        print("=" * 70)
        print("Creating user...")
        user_data = UserCreate(
            email="alice@example.com",
            username="alice",
            full_name="Alice Smith",
            password="securepass123"
        )
        user = create_user(db, user_data)
        print(f"✓ Created user: {user.username} (ID: {user.id})")
        print(f"  Email: {user.email}")
        print(f"  Note: Password is hashed and NOT in response")
        
        # Create posts
        print("\n" + "=" * 70)
        print("Creating posts...")
        post1 = PostCreate(
            title="My First Post",
            content="This is my first blog post!",
            published=True
        )
        post1_response = create_post(db, post1, user.id)
        print(f"✓ Created post: {post1_response.title}")
        
        post2 = PostCreate(
            title="Draft Post",
            content="This is a draft",
            published=False
        )
        post2_response = create_post(db, post2, user.id)
        print(f"✓ Created post: {post2_response.title} (published: {post2_response.published})")
        
        # Get user's posts
        print("\n" + "=" * 70)
        print(f"Getting posts for user {user.username}...")
        posts = get_posts_by_user(db, user.id)
        print(f"✓ Found {len(posts)} posts")
        for post in posts:
            print(f"  - {post.title} (ID: {post.id})")
        
        # Validation example
        print("\n" + "=" * 70)
        print("Testing validation...")
        try:
            invalid_user = UserCreate(
                email="not-an-email",
                username="ab",  # Too short
                password="short"  # Too short
            )
        except Exception as e:
            print(f"✓ Validation caught errors: {type(e).__name__}")
            print(f"  Pydantic prevents invalid data from reaching database")


if __name__ == "__main__":
    main()
