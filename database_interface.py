from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemy.orm import DeclarativeBase, mapped_column, Relationship, MappedAsDataclass, Mapped
from sqlalchemy import String, Integer, ForeignKey
from typing import List, Optional
from datetime import datetime

# import legacy_interface


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class Customer(Base):                   # Currently only stores information needed to contact + ship
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]                   # Client name
    email: Mapped[str]                  # Email
    address1: Mapped[str]               # Client street address
    address2: Mapped[str]               # Client city/state


class Order(Base):                                                                  # Source of the order invoice
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[str]                                                             # Something like [received, awaiting_stock, in_progress, shipped]
    created: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)      # When was the order received
    finished: Mapped[Optional[datetime]] = mapped_column(default_factory=datetime)  # When was the order completed
    pricing_model_id: Mapped[int] = mapped_column(ForeignKey("fees.id"))
    calculated_cost: Mapped[float]                                                  # Just store the calculated cost for ease


class OrderItem(Base):                                                  # Each item included in an order
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"))
    quantity: Mapped[int]                                               # Num of items in the order
    status: Mapped[str]                                                 # Status such as [missing_stock, collecting, ready]


class Inventory(Base):                                              # Stores current state of the stock of every item in inventory
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    legacy_id: Mapped[int] = mapped_column(ForeignKey("parts.id"))  # Id of item in legacy database
    stock: Mapped[int]                                              # Current num of available stock


class FeeBrackets(Base):
    __tablename__ = "fee_brackets"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]                               # Bracket info
    min_weight: Mapped[Optional[float]]             # Min and max weights for the current bracket type
    max_weight: Mapped[Optional[float]]


class Fees(Base):
    __tablename__ = "fees"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    description: Mapped[str]                                                # Helper text (maybe delete and just use fees.bracket?)
    bracket: Mapped[int] = mapped_column(ForeignKey("fee_brackets.id"))     # What bracket do we use to properly apply our fees
    base_charge: Mapped[float]                                              # Base order charge
    weight_m: Mapped[float]                                                 # These parameters follow the y = mx + b pattern
    weight_b: Mapped[float]
    # shipping_m: Mapped[float]              # I don't think we should worry about this in here
    # shipping_b: Mapped[float]




ENGINE = create_engine("sqlite:///data.db")




