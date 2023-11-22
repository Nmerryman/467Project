from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemy.orm import DeclarativeBase, mapped_column, Relationship, MappedAsDataclass, Mapped
from sqlalchemy import String, Integer, ForeignKey
from typing import List, Optional
from datetime import datetime

from sqlalchemy import insert

import legacy_interface


Base = legacy_interface.Base    # Make sure we use the same Base as the other tables to avoid any issues


class Customer(Base):                   # Currently only stores information needed to contact + ship
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]                   # Client name
    email: Mapped[str]                  # Email
    address1: Mapped[str]               # Client street address
    address2: Mapped[str]               # Client city/state


class Order(Base):                                                                  # Source of the order invoice
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[str]                                                     # Something like [received, awaiting_stock, in_progress, shipped]
    created: Mapped[datetime]                                               # When was the order received
    finished: Mapped[Optional[datetime]]                                    # When was the order completed
    pricing_model_id: Mapped[int] = mapped_column(ForeignKey("fees.id"))
    calculated_cost: Mapped[float]                                          # Just store the calculated cost for ease


class OrderItem(Base):                                                  # Each item included in an order
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"))
    quantity: Mapped[int]                                               # Num of items in the order
    status: Mapped[str]                                                 # Status such as [missing_stock, collecting, ready]
    cost: Mapped[float]                                                 # Store a precalculated value for cost


class Inventory(Base):                                              # Stores current state of the stock of every item in inventory
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    legacy_id: Mapped[int] = mapped_column(ForeignKey("parts.number"))  # Id of item in legacy database
    stock: Mapped[int]                                              # Current num of available stock


class FeeBrackets(Base):
    __tablename__ = "fee_brackets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]                               # Bracket info
    min_weight: Mapped[Optional[float]]             # Min and max weights for the current bracket type
    max_weight: Mapped[Optional[float]]


class Fees(Base):
    __tablename__ = "fees"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str]                                                # Helper text (maybe delete and just use fees.bracket?)
    bracket: Mapped[int] = mapped_column(ForeignKey("fee_brackets.id"))     # What bracket do we use to properly apply our fees
    base_charge: Mapped[float]                                              # Base order charge
    weight_m: Mapped[float]                                                 # These parameters follow the y = mx + b pattern
    weight_b: Mapped[float]
    # shipping_m: Mapped[float]              # I don't think we should worry about this in here
    # shipping_b: Mapped[float]


ENGINE = create_engine("sqlite:///test.db")
Base.metadata.create_all(ENGINE)


def gen_dev_customer():
    # Generates a test user
    with Session(ENGINE) as session:
        session.execute(insert(Customer).values(name="test", email="a@b.c", address1="123 street", address2="Bajookie land"))
        session.commit()


def sec(statement, commit=True):
    """
    Session - Execute - Commit
    Shorthand because I'm lazy
    """
    with Session(ENGINE) as session:
        res = session.execute(statement)
        if commit:
            session.commit()
    return res


def main():
    # gen_dev_customer()
    stmt = insert(Customer).values(name="a", email="B", address1="1", address2="2")
    sec(stmt)



if __name__ == '__main__':
    main()

