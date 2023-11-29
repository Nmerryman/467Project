from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, MappedAsDataclass, Mapped
from sqlalchemy import String, Integer, ForeignKey
from typing import List, Optional
from datetime import datetime

from sqlalchemy import insert, select, update

import legacy_interface


Base = legacy_interface.Base    # Make sure we use the same Base as the other tables to avoid any issues


class Customer(Base):                   # Currently only stores information needed to contact + ship
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]                   # Client name
    email: Mapped[str]                  # Email
    address1: Mapped[str]               # Client street address
    address2: Mapped[str]               # Client city/state

    def __repr__(self):
        return f"Customer[{self.id}](name={self.name}, email={self.email}: addr1={self.address1} addr2={self.address2})"


class Order(Base):                                                                  # Source of the order invoice
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[str]                                                     # Something like [received, awaiting_stock, in_progress, shipped]
    created: Mapped[datetime]                                               # When was the order received
    finished: Mapped[Optional[datetime]]                                    # When was the order completed
    pricing_model_id: Mapped[Optional[int]] = mapped_column(ForeignKey("fees.id"))
    total_weight: Mapped[Optional[float]]
    calculated_cost: Mapped[Optional[float]]                                          # Just store the calculated cost for ease

    customer: Mapped[Customer] = relationship(lazy="joined")
    pricing_model: Mapped["Fees"] = relationship(lazy="joined")

    def __repr__(self) -> str:
        return f"Order[{self.id}](cust_id={self.customer_id}, status={self.status}, created={self.created}, finished={self.finished}, pricing_id={self.pricing_model_id}, calc_cost={self.calculated_cost})"


class OrderItem(Base):                                                  # Each item included in an order
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"))
    quantity: Mapped[int]                                               # Num of items in the order
    status: Mapped[str]                                                 # Status such as [missing_stock, collecting, ready]
    cost: Mapped[Optional[float]]                                       # Store a precalculated value for cost
    weight: Mapped[Optional[float]]

    order: Mapped[Order] = relationship(lazy="joined")
    item: Mapped["Inventory"] = relationship(lazy="joined")

    def __repr__(self) -> str:
        return f"OrderItem[{self.id}](order={self.order_id}, item_id={self.item_id}, quantity={self.quantity}, status={self.status}, cost={self.cost})"


class Inventory(Base):                                              # Stores current state of the stock of every item in inventory
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    legacy_id: Mapped[int] = mapped_column(ForeignKey("parts.number"))  # Id of item in legacy database
    stock: Mapped[int]                                              # Current num of available stock

    def __repr__(self) -> str:
        return f"Inventory[{self.id}](legacy_id={self.legacy_id}, stock={self.stock})"


class FeeBrackets(Base):
    __tablename__ = "fee_brackets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]                               # Bracket info
    min_weight: Mapped[float]                       # Min and max weights for the current bracket type
    max_weight: Mapped[float]
    base_charge: Mapped[float]                      # Base bracket charge



class Fees(Base):
    __tablename__ = "fees"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str]                                                # Helper text (maybe delete and just use fees.bracket?)
    bracket_id: Mapped[int] = mapped_column(ForeignKey("fee_brackets.id"))     # What bracket do we use to properly apply our fees
    weight_m: Mapped[float]                                                 # These parameters follow the y = mx + b pattern
    weight_b: Mapped[float]
    
    bracket: Mapped[FeeBrackets] = relationship(lazy="joined")


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


def full_table(table: Base):
    with Session(ENGINE) as session:
        query = select(table)
        return session.execute(query).scalars().all()


def _from_id(table: Base, id_num: int):
    with Session(ENGINE) as session:
        query = select(table).where(table.id == id_num)
        return session.execute(query).scalar()


def customer_new(name: str, email: str, addr1: str, addr2: str) -> int:
    with Session(ENGINE) as session:
        cust = Customer(name=name, email=email, address1=addr1, address2=addr2)
        session.add(cust)
        session.commit()
        return cust.id


def customer_from_id(cust_id: int):
    return _from_id(Customer, cust_id)


def customer_update(cust_id: int, **kwargs):
    """
    To set wkargs, simply call customer_update(10, name="newname")
    """
    with Session(ENGINE) as session:
        query = update(Customer).where(Customer.id == cust_id).values(**kwargs)
        session.execute(query)
        session.commit()


def order_new(cust_id: int, status: str, pricing_m_id: int, created: datetime, finished=None, calc_cost=0.0):
    with Session(ENGINE) as session:
        order = Order(customer_id=cust_id, status=status, created=created, finished=finished, pricing_model_id=pricing_m_id, calculated_cost=calc_cost)
        session.add(order)
        session.commit()
        return order.id


def order_from_id(order_id: int):
    return _from_id(Order, order_id)


def order_update(order_id: int, **kwargs):
    with Session(ENGINE) as session:
        query = update(Order).where(Order.id == order_id).values(**kwargs)
        session.execute(query)
        session.commit()


def order_item_new(order_id: int, item_id: int, quantity: int, status: str, cost: float):
    with Session(ENGINE) as session:
        order_item = OrderItem(order_id=order_id, item_id=item_id, quantity=quantity, status=status, cost=cost)
        session.add(order_item)
        session.commit()
        return order_item.id


def order_item_from_id(oi_id: int):
    return _from_id(OrderItem, oi_id)


def order_item_update(oi_id: int, **kwargs):
    with Session(ENGINE) as session:
        query = update(OrderItem).where(OrderItem.id == oi_id).values(**kwargs)
        session.execute(query)
        session.commit()


def inventory_new(legacy_id: int, stock: int = 0):
    with Session(ENGINE) as session:
        inventory = Inventory(legacy_id=legacy_id, stock=stock)
        session.add(inventory)
        session.commit()
        return inventory.id


def inventory_from_id(i_id: int):
    return _from_id(Inventory, i_id)


def inventory_update(i_id: int, **kwargs):
    with Session(ENGINE) as session:
        query = update(Inventory).where(Inventory.id == i_id).values(**kwargs)
        session.execute(query)
        session.commit()


def fee_bracket_new(name: str, min_weight: float = None, max_weight: float = None):
    with Session(ENGINE) as session:
        bracket = FeeBrackets(name=name, min_weight=min_weight, max_weight=max_weight)
        session.add(bracket)
        session.commit()
        return bracket.id


def fee_bracket_from_id(fb_id: int):
    return _from_id(FeeBrackets, fb_id)


def fee_bracket_update(fb_id: int, **kwargs):
    with Session(ENGINE) as session:
        query = update(FeeBrackets).where(FeeBrackets.id == fb_id).values(**kwargs)



def fee_new(description: str, bracket_id: int, base_charge: float, weight_m: float, weight_b: float):
    with Session(ENGINE) as session:
        fee = Fees(description=description, bracket_id=bracket_id, base_charge=base_charge, weight_m=weight_m, weight_b=weight_b)
        session.add(fee)
        session.commit()
        return fee.id


def fee_from_id(f_id: int):
    return _from_id(Fees, f_id)


def fee_update(f_id: int, **kwargs):
    with Session(ENGINE) as session:
        query = update(Fees).where(Fees.id == f_id).values(**kwargs)
        session.execute(query)
        session.commit()


def main():
    # gen_dev_customer()
    # stmt = insert(Customer).values(name="a", email="B", address1="1", address2="2")
    # sec(stmt)
    print("---- List full (basically) inventory table ----")
    print("\n".join(list(map(str, full_table(Inventory)))[0:20]))
    print("---- list an order object ----")
    test_order = order_from_id(2)
    print(test_order)
    print("---- Print it's joined customer object ----")
    print(test_order.customer)




if __name__ == '__main__':
    main()

