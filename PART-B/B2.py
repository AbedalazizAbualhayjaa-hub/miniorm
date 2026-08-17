from sqlalchemy import (
    String,
    ForeignKey,
    create_engine,
    select,
    event
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
    selectinload
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    posts: Mapped[list["Post"]] = relationship(
        back_populates="author"
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    title: Mapped[str] = mapped_column(String(200))

    author: Mapped["User"] = relationship(
        back_populates="posts"
    )


engine = create_engine(
    "sqlite:///:memory:",
    echo=True
)

Base.metadata.create_all(engine)


# Seed 30 users + 30 posts

with Session(engine) as session:

    for i in range(1, 31):

        user = User(name=f"User {i}")

        user.posts.append(
            Post(title=f"Post {i}")
        )

        session.add(user)

    session.commit()


# SQL statement counter

query_count = 0


def count_queries(
    conn,
    cursor,
    statement,
    parameters,
    context,
    executemany
):
    global query_count

    if statement.lstrip().upper().startswith("SELECT"):
        query_count += 1


event.listen(
    engine,
    "before_cursor_execute",
    count_queries
)


# NAIVE VERSION — N+1

query_count = 0

with Session(engine) as session:

    users = session.scalars(
        select(User)
    ).all()

    for user in users:
        print(
            user.name,
            "- posts:",
            len(user.posts)
        )


naive_count = query_count


# FIXED VERSION — selectinload

query_count = 0

with Session(engine) as session:

    users = session.scalars(
        select(User).options(
            selectinload(User.posts)
        )
    ).all()

    for user in users:
        print(
            user.name,
            "- posts:",
            len(user.posts)
        )


fixed_count = query_count

# Deliverable

print("\n-------------------------")
print("Task B2 Results")
print("-------------------------")

print(
    "Naive query count:",
    naive_count
)

print(
    "With selectinload:",
    fixed_count
)

print(
    "\nFix used:"
)

print(
    "select(User).options("
    "selectinload(User.posts))"
)
