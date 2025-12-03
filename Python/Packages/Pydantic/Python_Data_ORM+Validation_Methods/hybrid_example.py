"""
Example 3: Hybrid Approach (SQLAlchemy 2.0 + Pydantic with Shared Base)
Balance between separation and code reuse
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# ============================================================================
# SQLAlchemy 2.0 Models (using modern mapped_column style)
# ============================================================================

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships with type hints
    posts: Mapped[List["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = 'posts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(default=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author: Mapped["User"] = relationship(back_populates="posts")


# ============================================================================
# Pydantic Models (with shared base classes for DRY)
# ============================================================================

# Shared base schemas
class UserBaseSchema(BaseModel):
    """Shared user fields"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: Optional[str] = None


class PostBaseSchema(BaseModel):
    """Shared post fields"""
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    published: bool = False


# Input schemas
class UserCreate(UserBaseSchema):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class PostCreate(PostBaseSchema):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


# Response schemas
class UserResponse(UserBaseSchema):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PostResponse(PostBaseSchema):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserWithPosts(UserResponse):
    posts: List[PostResponse] = []


class PostWithAuthor(PostResponse):
    author: UserResponse


# ============================================================================
# CRUD Operations (with modern SQLAlchemy 2.0 patterns)
# ============================================================================

def hash_password(password: str) -> str:
    """Simulate password hashing"""
    return f"hashed_{password}"


def create_user(db: Session, user: UserCreate) -> UserResponse:
    """Create a new user"""
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.model_validate(db_user)


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
    """Update a user"""
    db_user = db.get(User, user_id)
    if not db_user:
        return None
    
    # Only update provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    if 'password' in update_data:
        update_data['hashed_password'] = hash_password(update_data.pop('password'))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.model_validate(db_user)


def create_post(db: Session, post: PostCreate, author_id: int) -> PostResponse:
    """Create a new post"""
    db_post = Post(
        title=post.title,
        content=post.content,
        published=post.published,
        author_id=author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return PostResponse.model_validate(db_post)


def get_user_with_posts(db: Session, user_id: int) -> Optional[UserWithPosts]:
    """Get user with all their posts"""
    db_user = db.get(User, user_id)
    if db_user:
        return UserWithPosts.model_validate(db_user)
    return None


# ============================================================================
# Demo Usage
# ============================================================================

def main():
    # Setup database
    engine = create_engine('sqlite:///hybrid.db', echo=False)
    Base.metadata.create_all(engine)
    
    with Session(engine) as db:
        # Create user
        print("=" * 70)
        print("Creating user...")
        user_data = UserCreate(
            email="carol@example.com",
            username="carol",
            full_name="Carol Williams",
            password="securepass123"
        )
        user = create_user(db, user_data)
        print(f"✓ Created user: {user.username} (ID: {user.id})")
        
        # Update user
        print("\n" + "=" * 70)
        print("Updating user...")
        user_update = UserUpdate(full_name="Carol M. Williams")
        updated_user = update_user(db, user.id, user_update)
        if updated_user:
            print(f"✓ Updated user: {updated_user.full_name}")
        
        # Create posts
        print("\n" + "=" * 70)
        print("Creating posts...")
        post1 = PostCreate(
            title="Hybrid Approach Benefits",
            content="Gets the best of both worlds!",
            published=True
        )
        create_post(db, post1, user.id)
        
        post2 = PostCreate(
            title="SQLAlchemy 2.0 Features",
            content="Modern type hints and better patterns",
            published=True
        )
        create_post(db, post2, user.id)
        
        # Get user with posts
        print("\n" + "=" * 70)
        print("Getting user with posts...")
        user_with_posts = get_user_with_posts(db, user.id)
        if user_with_posts:
            print(f"✓ User: {user_with_posts.username}")
            print(f"  Full name: {user_with_posts.full_name}")
            print(f"  Posts: {len(user_with_posts.posts)}")
            for post in user_with_posts.posts:
                print(f"    - {post.title} (published: {post.published})")
        
        print("\n" + "=" * 70)
        print("This approach combines:")
        print("  ✓ Modern SQLAlchemy 2.0 features (type hints, mapped_column)")
        print("  ✓ Clear separation between DB and API layers")
        print("  ✓ Pydantic validation and serialization")
        print("  ✓ Shared base schemas to reduce duplication")


if __name__ == "__main__":
    main()
