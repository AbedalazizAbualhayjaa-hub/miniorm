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


# Task A2
class Boolean(Field):
    def __init__(self, **kw):
        super().__init__("INTEGER", **kw)


# Deliverable test
published = Boolean(default=0)
published.name = "published"

print("Generated DDL:", published.ddl())
print("Default value:", published.default)
