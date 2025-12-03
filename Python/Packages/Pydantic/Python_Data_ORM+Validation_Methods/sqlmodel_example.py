"""
Example 2: SQLModel (Combined Approach)
Single models that work as both Pydantic validators AND SQLAlchemy tables
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select

# ============================================================================
# SQLModel Models (Combined Database + Validation)
# ============================================================================

# Base models (shared fields)
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    username: str = Field(min_length=3, max_length=50, unique=True)
    full_name: Optional[str] = None


class PostBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    published: bool = False


# Database models (table=True)
class User(UserBase, table=True):
    __tablename__ = 'users'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    posts: List["Post"] = Relationship(back_populates="author", cascade_delete=True)


class Post(PostBase, table=True):
    __tablename__ = 'posts'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    author: Optional[User] = Relationship(back_populates="posts")


# Input models (for creation)
class UserCreate(UserBase):
    password: str = Field(min_length=8)


class PostCreate(PostBase):
    pass


# Response models (for API responses)
class UserRead(UserBase):
    id: int
    created_at: datetime


class PostRead(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime


class UserReadWithPosts(UserRead):
    posts: List[PostRead] = []


class PostReadWithAuthor(PostRead):
    author: UserRead


# ============================================================================
# CRUD Operations
# ============================================================================

def hash_password(password: str) -> str:
    """Simulate password hashing"""
    return f"hashed_{password}"


def create_user(session: Session, user: UserCreate) -> UserRead:
    """Create a new user"""
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hash_password(user.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    # Convert to response model
    return UserRead.model_validate(db_user)


def get_user(session: Session, user_id: int) -> Optional[UserRead]:
    """Get user by ID"""
    user = session.get(User, user_id)
    if user:
        return UserRead.model_validate(user)
    return None


def create_post(session: Session, post: PostCreate, author_id: int) -> PostRead:
    """Create a new post"""
    db_post = Post(
        title=post.title,
        content=post.content,
        published=post.published,
        author_id=author_id
    )
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    
    return PostRead.model_validate(db_post)


def get_posts_by_user(session: Session, user_id: int) -> List[PostRead]:
    """Get all posts by a user"""
    statement = select(Post).where(Post.author_id == user_id)
    posts = session.exec(statement).all()
    return [PostRead.model_validate(post) for post in posts]


def get_user_with_posts(session: Session, user_id: int) -> Optional[UserReadWithPosts]:
    """Get user with all their posts"""
    user = session.get(User, user_id)
    if user:
        return UserReadWithPosts.model_validate(user)
    return None


# ============================================================================
# Demo Usage
# ============================================================================

def main():
    # Setup database
    engine = create_engine('sqlite:///sqlmodel.db', echo=False)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Create user
        print("=" * 70)
        print("Creating user...")
        user_data = UserCreate(
            email="bob@example.com",
            username="bob",
            full_name="Bob Johnson",
            password="securepass123"
        )
        user = create_user(session, user_data)
        print(f"✓ Created user: {user.username} (ID: {user.id})")
        print(f"  Email: {user.email}")
        print(f"  Note: Password is hashed and NOT in response")
        
        # Create posts
        print("\n" + "=" * 70)
        print("Creating posts...")
        post1 = PostCreate(
            title="SQLModel is Cool",
            content="Less boilerplate than separate models!",
            published=True
        )
        post1_response = create_post(session, post1, user.id)
        print(f"✓ Created post: {post1_response.title}")
        
        post2 = PostCreate(
            title="Draft Tutorial",
            content="How to use SQLModel effectively",
            published=False
        )
        post2_response = create_post(session, post2, user.id)
        print(f"✓ Created post: {post2_response.title} (published: {post2_response.published})")
        
        # Get user's posts
        print("\n" + "=" * 70)
        print(f"Getting posts for user {user.username}...")
        posts = get_posts_by_user(session, user.id)
        print(f"✓ Found {len(posts)} posts")
        for post in posts:
            print(f"  - {post.title} (ID: {post.id})")
        
        # Get user with posts (using relationship)
        print("\n" + "=" * 70)
        print("Getting user with posts (using relationship)...")
        user_with_posts = get_user_with_posts(session, user.id)
        if user_with_posts:
            print(f"✓ User: {user_with_posts.username}")
            print(f"  Posts: {len(user_with_posts.posts)}")
            for post in user_with_posts.posts:
                print(f"    - {post.title}")
        
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
            print(f"  SQLModel provides same validation as Pydantic")


if __name__ == "__main__":
    main()
