from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, MappedAsDataclass, Mapped
from sqlalchemy import String, Integer, ForeignKey
from typing import List, Optional
from datetime import datetime

from sqlalchemy import insert, select, update, and_

import legacy_interface
from legacy_interface import LegacyParts, ask_legacy, post_scalars

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
    fee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("fees.id"))
    total_weight: Mapped[Optional[float]]
    total_cost: Mapped[Optional[float]]                                          # Just store the calculated cost for ease
    total_cost_post_fee: Mapped[Optional[float]]

    customer: Mapped[Customer] = relationship(lazy="joined")
    pricing_model: Mapped["Fees"] = relationship(lazy="joined")

    def __repr__(self) -> str:
        return f"Order[{self.id}](cust_id={self.customer_id}, status={self.status}, created={self.created}, finished={self.finished}, fee_id={self.fee_id}, (${self.total_cost}->${self.total_cost_post_fee}, {self.total_weight}lb) )"


class OrderItem(Base):                                                  # Each item included in an order
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"))
    quantity: Mapped[int]                                               # Num of items in the order
    cost: Mapped[Optional[float]]                                       # Store a precalculated value for cost
    weight: Mapped[Optional[float]]

    order: Mapped[Order] = relationship(lazy="joined")
    item: Mapped["Inventory"] = relationship(lazy="joined")

    def __repr__(self) -> str:
        return f"OrderItem[{self.id}](order={self.order_id}, item_id={self.item_id}, quantity={self.quantity}, cost={self.cost})"


class Inventory(Base):                                              # Stores current state of the stock of every item in inventory
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    legacy_id: Mapped[int] = mapped_column(ForeignKey("parts.number"))  # Id of item in legacy database
    stock: Mapped[int]                                              # Current num of available stock

    def __repr__(self) -> str:
        return f"Inventory[{self.id}](legacy_id={self.legacy_id}, stock={self.stock})"


class Fees(Base):
    __tablename__ = "fees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]                                                # Helper text (maybe delete and just use fees.bracket?)
    weight_m: Mapped[float]                                                 # These parameters follow the y = mx + b pattern
    weight_b: Mapped[float]
    min_weight: Mapped[float]
    max_weight: Mapped[float]

    def __repr__(self) -> str:
        return f"Fee[{self.id}](name={self.name}, (y={self.weight_m}x+{self.weight_b}), ({self.min_weight}<=x<{self.max_weight}))"


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


def order_new(cust_id: int, status: str, created: datetime = datetime.now()):
    with Session(ENGINE) as session:
        order = Order(customer_id=cust_id, status=status, created=created)
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


def order_not_done():
    with Session(ENGINE) as session:
        query = select(Order).where(Order.status != "Shipped")

        res = []
        for a in session.execute(query).scalars().all():
            # temp =
            res.append(a)
        return res


def order_item_new(order_id: int, item_id: int, quantity: int):
    with Session(ENGINE) as session:
        order_item = OrderItem(order_id=order_id, item_id=item_id, quantity=quantity)
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


def order_item_not_done():
    # We return and OrderItem but grafted a LegacyParts object on OrderItem.legacy
    with Session(ENGINE) as session:
        query = select(OrderItem, Inventory.legacy_id).join(Order).where(Order.status != "Shipped").join(Inventory)
        temp = session.execute(query).all()
        # print(temp)

        res = []
        for a, b in temp:
            a.legacy = post_scalars(ask_legacy(select(LegacyParts).where(LegacyParts.number == b)))[0]
            res.append(a)
        return res


def order_items_from_order(o_id: int):
    with Session(ENGINE) as session:
        query = select(OrderItem).where(Order.id == o_id).join(Order)
        return session.execute(query).scalars().all()


def inventory_new(legacy_id: int, stock: int = 0):
    with Session(ENGINE) as session:
        inventory = Inventory(legacy_id=legacy_id, stock=stock)
        session.add(inventory)
        session.commit()
        return inventory.id


def inventory_from_id(i_id: int):
    return _from_id(Inventory, i_id)


def inventory_from_legacy_id(legacy_id: int):
    """
    Fetch inventory record for a specific legacy_id.
    """
    with Session(ENGINE) as session:
        result = session.execute(select(Inventory).where(Inventory.legacy_id == legacy_id)).scalar()
        return result

def inventory_update(i_id: int, **kwargs):
    with Session(ENGINE) as session:
        query = update(Inventory).where(Inventory.id == i_id).values(**kwargs)
        session.execute(query)
        session.commit()


def fee_new(name: str, bracket_id: int, base_charge: float, weight_m: float, weight_b: float, min_w: float, max_w: float):
    with Session(ENGINE) as session:
        fee = Fees(name=name, bracket_id=bracket_id, base_charge=base_charge, weight_m=weight_m, weight_b=weight_b, min_weight=min_w, max_weight=max_w)
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


def legacy_from_order_item_id(oi_id: int):
    with Session(ENGINE) as session:
        query = select(Inventory.legacy_id).join(OrderItem).where(OrderItem.id == oi_id)
        leg_id = session.execute(query).scalar_one()
        return post_scalars(ask_legacy(select(LegacyParts).where(LegacyParts.number == leg_id)))[0]


def evaluate_missing_costnweight():
    # Update the weights/price values of each OrderItem if it's not set
    with Session(ENGINE) as session:
        # Update the price and weight of each order item if it's missing.
        for a in session.execute(select(OrderItem).where(OrderItem.cost.is_(None))).scalars().all():
            part_weight, part_price = post_scalars(
                ask_legacy(select(LegacyParts.weight, LegacyParts.price).where(LegacyParts.number == a.item_id)))

            a.cost = part_price * a.quantity
            a.weight = part_weight * a.quantity

        session.commit()

    print(*full_table(OrderItem), sep="\n")


def update_order_weight():
    # Update all weights/prices for every Order + OrderItem in the db
    # We do all at once because it's then we know it will always be correct
    with Session(ENGINE) as session:
        for a in session.execute(select(Order)).scalars():
            sum_price = 0
            sum_weight = 0
            for b in session.execute(select(OrderItem).where(OrderItem.order_id == a.id)).scalars():
                part_price, part_weight = post_scalars(
                    ask_legacy(select(LegacyParts.price, LegacyParts.weight).where(LegacyParts.number == b.item_id)))
                b.cost = part_price * b.quantity
                b.weight = part_weight * b.quantity
                sum_price += part_price * b.quantity
                sum_weight += part_weight * b.quantity
                # print(b)

            a.total_cost = sum_price
            a.total_weight = sum_weight

            fee = session.execute(
                select(Fees).where(and_(Fees.min_weight <= sum_weight, Fees.max_weight > sum_weight))).scalar()
            if fee:
                # print(fee)
                a.fee_id = fee.id
                a.total_cost_post_fee = a.total_cost + fee.weight_m * a.total_weight + fee.weight_b
            else:
                print("No fee found for order", a.id)
            print(a)

        session.commit()


def main():
    # gen_dev_customer()
    # stmt = insert(Customer).values(name="a", email="B", address1="1", address2="2")
    # sec(stmt)
    print("---- List full (basically) inventory table ----")
    print("\n".join(list(map(str, full_table(Inventory)))[0:20]))
    # print("---- list an order object ----")
    # test_order = order_from_id(2)
    # print(test_order)
    # print("---- Print it's joined customer object ----")
    # print(test_order.customer)
    print ("---- Legacy ID, stock ----")
    print(inventory_from_legacy_id(1))


if __name__ == '__main__':
    main()

