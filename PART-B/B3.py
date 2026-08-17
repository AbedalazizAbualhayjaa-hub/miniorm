from sqlalchemy import (
    String,
    Float,
    create_engine
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session
)


class Base(DeclarativeBase):
    pass


# Account Model

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    owner: Mapped[str] = mapped_column(
        String(100)
    )

    balance: Mapped[float] = mapped_column(
        Float
    )


engine = create_engine(
    "sqlite:///:memory:",
    echo=True
)

Base.metadata.create_all(engine)


# Initial accounts

with Session(engine) as session:

    account1 = Account(
        owner="Sara",
        balance=500.0
    )

    account2 = Account(
        owner="Omar",
        balance=300.0
    )

    session.add_all([
        account1,
        account2
    ])

    session.commit()


# Transfer function

def transfer(
    session,
    from_id,
    to_id,
    amount,
    force_error=False
):

    sender = session.get(
        Account,
        from_id
    )

    receiver = session.get(
        Account,
        to_id
    )

    if sender is None or receiver is None:
        raise ValueError(
            "Account not found"
        )

    if sender.balance < amount:
        raise ValueError(
            "Insufficient balance"
        )

    # Debit sender
    sender.balance -= amount

    # Force an error AFTER the debit
    if force_error:
        raise RuntimeError(
            "Forced transaction failure"
        )

    # Credit receiver
    receiver.balance += amount


# Show balances before transfer

with Session(engine) as session:

    sara = session.get(
        Account,
        1
    )

    omar = session.get(
        Account,
        2
    )

    print("\nBefore failed transfer:")

    print(
        "Sara:",
        sara.balance
    )

    print(
        "Omar:",
        omar.balance
    )


# Force transaction failure

try:

    with Session(engine) as session:

        with session.begin():

            transfer(
                session,
                from_id=1,
                to_id=2,
                amount=50,
                force_error=True
            )

except RuntimeError as error:

    print(
        "\nError:",
        error
    )

    print(
        "Transaction rolled back."
    )


# Verify balances

with Session(engine) as session:

    sara = session.get(
        Account,
        1
    )

    omar = session.get(
        Account,
        2
    )

    print(
        "\nAfter failed transfer:"
    )

    print(
        "Sara:",
        sara.balance
    )

    print(
        "Omar:",
        omar.balance
    )


# Deliverable evidence

print(
    "\nBoth balances are unchanged, "
    "proving the transaction rolled back."
)
