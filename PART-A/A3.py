# Field classes from Task A2

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


# Task A3 - Metaclass

class ModelMeta(type):
    def __new__(mcs, name, bases, ns):
        fields = {}

        for key, val in list(ns.items()):
            if isinstance(val, Field):
                # Automatically give the field its column name
                val.name = key
                fields[key] = val

        cls = super().__new__(mcs, name, bases, ns)

        cls._fields = fields
        cls._table = ns.get("__table__", name.lower())

        return cls


# User model

class User(metaclass=ModelMeta):
    id = Integer(primary_key=True)
    name = Text(nullable=False)
    email = Text(unique=True)


# Deliverable


print("User._fields:")
print(User._fields)

print("\nUser._table:")
print(User._table)

print("\nField names assigned by the metaclass:")

for field_name, field in User._fields.items():
    print(field_name, "->", field.name)
