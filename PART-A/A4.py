import sqlite3


# Field classes

class Field:
    def __init__(
        self,
        col_type,
        primary_key=False,
        nullable=True,
        unique=False,
        default=None
    ):
        self.col_type = col_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique
        self.default = default
        self.name = None

    def ddl(self):
        parts = [self.name, self.col_type]

        if self.primary_key:
            parts.append("PRIMARY KEY")

        if not self.nullable and not self.primary_key:
            parts.append("NOT NULL")

        if self.unique:
            parts.append("UNIQUE")

        return " ".join(parts)


class Integer(Field):
    def __init__(self, **kw):
        super().__init__("INTEGER", **kw)


class Text(Field):
    def __init__(self, **kw):
        super().__init__("TEXT", **kw)


class Real(Field):
    def __init__(self, **kw):
        super().__init__("REAL", **kw)


class Boolean(Field):
    def __init__(self, **kw):
        super().__init__("INTEGER", **kw)


# Metaclass

class ModelMeta(type):
    def __new__(mcs, name, bases, ns):
        fields = {}

        for key, val in list(ns.items()):
            if isinstance(val, Field):
                val.name = key
                fields[key] = val

        cls = super().__new__(mcs, name, bases, ns)

        cls._fields = fields
        cls._table = ns.get("__table__", name.lower())

        return cls


# Database connection

_connection = None


def connect(path):
    global _connection

    _connection = sqlite3.connect(path)
    _connection.row_factory = sqlite3.Row
    _connection.execute("PRAGMA foreign_keys = ON")

    return _connection


# Base Model

class Model(metaclass=ModelMeta):

    def __init__(self, **kwargs):
        for fname, field in self._fields.items():
            setattr(
                self,
                fname,
                kwargs.get(fname, field.default)
            )

    @classmethod
    def create_table(cls):
        cols = ", ".join(
            field.ddl()
            for field in cls._fields.values()
        )

        _connection.execute(
            f"CREATE TABLE IF NOT EXISTS {cls._table} ({cols})"
        )

        _connection.commit()

    @classmethod
    def _pk_name(cls):
        for name, field in cls._fields.items():
            if field.primary_key:
                return name

        return "id"

    def save(self):
        pk = self._pk_name()

        cols = [
            name
            for name in self._fields
            if not (
                name == pk
                and getattr(self, name) is None
            )
        ]

        # INSERT
        if getattr(self, pk) is None:

            placeholders = ", ".join(
                "?" for _ in cols
            )

            values = [
                getattr(self, column)
                for column in cols
            ]

            cursor = _connection.execute(
                f"""
                INSERT INTO {self._table}
                ({', '.join(cols)})
                VALUES ({placeholders})
                """,
                values
            )

            # Store generated ID inside the object
            setattr(self, pk, cursor.lastrowid)

        # UPDATE
        else:

            assignments = ", ".join(
                f"{column} = ?"
                for column in cols
                if column != pk
            )

            values = [
                getattr(self, column)
                for column in cols
                if column != pk
            ]

            values.append(getattr(self, pk))

            _connection.execute(
                f"""
                UPDATE {self._table}
                SET {assignments}
                WHERE {pk} = ?
                """,
                values
            )

        _connection.commit()

        return self


# User Model

class User(Model):
    id = Integer(primary_key=True)
    name = Text(nullable=False)
    email = Text(unique=True)


# -----------------------------
# Task A4
# -----------------------------

connect(":memory:")

User.create_table()


# Create user with no ID
user = User(
    name="Sara",
    email="sara@example.com"
)

print("Before first save:")
print("ID:", user.id)


# First save -> INSERT
user.save()

print("\nAfter first save:")
print("ID:", user.id)
print("Name:", user.name)


# Change field
user.name = "Sara Updated"


# Second save -> UPDATE
user.save()


# Raw SQL verification

row_count = _connection.execute(
    "SELECT COUNT(*) FROM user"
).fetchone()[0]

row = _connection.execute(
    "SELECT * FROM user WHERE id = ?",
    (user.id,)
).fetchone()


print("\nAfter second save:")
print("Row count:", row_count)
print("ID:", row["id"])
print("Name:", row["name"])
print("Email:", row["email"])
