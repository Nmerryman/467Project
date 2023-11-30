from database_interface import *
from legacy_interface import ask_legacy, LegacyParts
from datetime import datetime

from sqlalchemy import select, update

import random  # We use random numbers because some the exact numbers of some values shouldn't matter
import faker

fake = faker.Faker()


def drop_tables():
    """
    Drop all tables
    """
    Base.metadata.drop_all(ENGINE)


def build_db():
    Base.metadata.create_all(ENGINE)

    with Session(ENGINE) as session:

        # Add legacy info
        for a in ask_legacy(select(LegacyParts)):
            temp_inventory = Inventory(legacy_id=a.number, stock=0 if random.random() > .5 else random.randint(0, 500))
            session.add(temp_inventory)

        # Add Fee styles for each weight
        session.add(Fees(name="Light packing", weight_m=3, weight_b=10, min_weight=0, max_weight=50))
        session.add(Fees(name="Standard packing", weight_m=3, weight_b=20, min_weight=50, max_weight=100))
        session.add(Fees(name="Heavy packing", weight_m=3, weight_b=30, min_weight=100, max_weight=1000))

        # Add old customers
        for _ in range(4):
            temp_address = fake.address().split('\n')
            session.add(Customer(name=fake.name(), email=fake.email(), address1=temp_address[0], address2=temp_address[1]))

        # Adding example orders
        session.add(Order(customer_id=1, status="Shipped", created=datetime(2020, 5, 17), finished=datetime(2020, 6, 5)))
        session.add(Order(customer_id=2, status="Shipped", created=datetime(2021, 5, 17), finished=datetime(2021, 6, 5)))
        session.add(Order(customer_id=3, status="In Progress", created=datetime(2022, 5, 17), finished=datetime(2024, 6, 5)))
        session.add(Order(customer_id=1, status="Waiting", created=datetime(2020, 5, 17)))

        # Add some items to the orders
        session.add(OrderItem(order_id=1, item_id=10, quantity=2, status="Packed"))
        session.add(OrderItem(order_id=1, item_id=12, quantity=1, status="Packed"))
        session.add(OrderItem(order_id=2, item_id=15, quantity=5, status="Packed"))
        session.add(OrderItem(order_id=3, item_id=20, quantity=2, status="Claimed"))
        session.add(OrderItem(order_id=3, item_id=30, quantity=2, status="Available"))

        session.commit()


def evaluate_costs():
    with Session(ENGINE) as session:
        # print(session.execute(select(OrderItem).where(OrderItem.cost.is_(None))).scalars().all())
        for a in session.execute(select(OrderItem).where(OrderItem.cost.is_(None))).scalars().all():
            print(ask_legacy(select(LegacyParts).where(LegacyParts.number == a.item_id)))

            print(a.item_id)
            # session.execute(update(LegacyParts).where(LegacyParts.number == a.item_id).values(cost=))



def main():
    # drop_tables()
    # build_db()
    evaluate_costs()



if __name__ == '__main__':
    main()
