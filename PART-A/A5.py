import sqlite3

# Fields

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


# Database

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
            name for name in self._fields
            if not (
                name == pk
                and getattr(self, name) is None
            )
        ]

        if getattr(self, pk) is None:

            placeholders = ", ".join("?" for _ in cols)

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

            setattr(self, pk, cursor.lastrowid)

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
            

        _connection.commit()
        return self

    # Convert database row -> Python object
    @classmethod
    def _from_row(cls, row):
        obj = cls()

        for fname in cls._fields:
            setattr(obj, fname, row[fname])

        return obj

    @classmethod
    def get(cls, pk):
        row = _connection.execute(
            f"""
            SELECT * FROM {cls._table}
            WHERE {cls._pk_name()} = ?
            """,
            (pk,)
        ).fetchone()

        return cls._from_row(row) if row else None

    @classmethod
    def all(cls):
        rows = _connection.execute(
            f"SELECT * FROM {cls._table}"
        ).fetchall()

        return [
            cls._from_row(row)
            for row in rows
        ]

    # Task A5

    @classmethod
    def filter(cls, **conditions):

        clauses = []
        values = []

        for key, value in conditions.items():

            # Greater than
            if key.endswith("__gt"):
                field_name = key[:-4]
                clauses.append(f"{field_name} > ?")

            # Less than
            elif key.endswith("__lt"):
                field_name = key[:-4]
                clauses.append(f"{field_name} < ?")

            # Normal equality
            else:
                field_name = key
                clauses.append(f"{field_name} = ?")

            values.append(value)

        sql = f"SELECT * FROM {cls._table}"

        if clauses:
            sql += " WHERE " + " AND ".join(clauses)

        rows = _connection.execute(
            sql,
            tuple(values)
        ).fetchall()

        return [
            cls._from_row(row)
            for row in rows
        ]


# User Model

class User(Model):
    id = Integer(primary_key=True)
    name = Text(nullable=False)
    email = Text(unique=True)
    age = Integer()


# -----------------------------
# Test A5
# -----------------------------

connect(":memory:")
User.create_table()

User(
    name="Sara",
    email="sara@example.com",
    age=22
).save()

User(
    name="Omar",
    email="omar@example.com",
    age=17
).save()

User(
    name="Lina",
    email="lina@example.com",
    age=30
).save()


# Deliverable query using __gt
adults = User.filter(age__gt=18)

print("Users older than 18:")

for user in adults:
    print(user.name, "-", user.age)


# Confirm __lt also works
young_users = User.filter(age__lt=18)

print("\nUsers younger than 18:")

for user in young_users:
    print(user.name, "-", user.age)
