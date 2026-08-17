from sqlalchemy import String, ForeignKey, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


# Base

class Base(DeclarativeBase):
    pass


# User Model

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(
        String(200),
        unique=True
    )

    posts: Mapped[list["Post"]] = relationship(
        back_populates="author"
    )


# Post Model

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    title: Mapped[str] = mapped_column(
        String(200)
    )

    author: Mapped["User"] = relationship(
        back_populates="posts"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post"
    )


# Comment Model

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id")
    )

    content: Mapped[str] = mapped_column(
        String(500)
    )

    post: Mapped["Post"] = relationship(
        back_populates="comments"
    )


# Database

engine = create_engine(
    "sqlite:///blog.db",
    echo=True
)


# Generate tables
Base.metadata.create_all(engine)


print("\nTables created successfully.")
