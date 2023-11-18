from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemy.orm import DeclarativeBase, mapped_column, Relationship, MappedAsDataclass, Mapped
from sqlalchemy import String, Integer, ForeignKey
from typing import List, Optional
from datetime import datetime

# import legacy_interface


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]                   # Client name
    email: Mapped[str]                  # Email
    address1: Mapped[str]               # Client street address
    address2: Mapped[str]               # Client city/state


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[str]
    created: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    finished: Mapped[Optional[datetime]] = mapped_column(default_factory=datetime)


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"))
    quantity: Mapped[int]


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    legacy_id: Mapped[int] = mapped_column(ForeignKey("parts.id"))
    stock: Mapped[int]





ENGINE = create_engine("sqlite:///data.db")




