import sqlite3

# Connect to an in-memory SQLite database
conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row


# USERS TABLE


conn.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
)
""")

# Insert Sara
conn.execute(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    ("Sara", "sara@x.com")
)

conn.commit()

# Fetch Sara
user = conn.execute(
    "SELECT * FROM users WHERE id = ?",
    (1,)
).fetchone()

print("User:", user["name"])


# POSTS TABLE

conn.execute("""
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# Insert two posts for Sara
conn.execute(
    "INSERT INTO posts (user_id, title) VALUES (?, ?)",
    (1, "My First Post")
)

conn.execute(
    "INSERT INTO posts (user_id, title) VALUES (?, ?)",
    (1, "Learning SQLite")
)

conn.commit()


# Fetch Sara's posts
posts = conn.execute(
    "SELECT * FROM posts WHERE user_id = ?",
    (1,)
).fetchall()

print("\nSara's Posts:")

for post in posts:
    print(post["id"], "-", post["title"])


# Deliverable note:
# The repeated CREATE, INSERT, SELECT, and parameter-handling code is the thing that I would want an ORM to eliminate.

conn.close()
