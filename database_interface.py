from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemy.orm import DeclarativeBase, mapped_column, Relationship
from sqlalchemy import String, Integer, ForeignKey
from typing import List


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)       # Client name
    address1 = mapped_column(String)   # Client street address
    address2 = mapped_column(String)   # Client city/state


class Order(Base):
    __tablename__ = "orders"

    id = mapped_column(Integer, primary_key=True)
    customer_id = mapped_column(Integer, ForeignKey("customers.id"))
    customer = Relationship("Customer")
    status = mapped_column(String)


    
class Inventory(Base):
    __tablename__ = "inventory"

    id = mapped_column(Integer, primary_key=True)
    legacy_id = mapped_column(Integer)
    amount = mapped_column(Integer)





ENGINE = create_engine("sqlite:///data.db")




