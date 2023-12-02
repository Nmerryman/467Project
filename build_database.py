from database_interface import *
from legacy_interface import ask_legacy, LegacyParts, post_scalars
from datetime import datetime

from sqlalchemy import select, update, and_

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
        # print(*ask_legacy(select(LegacyParts)), sep="\n")
        for a in post_scalars(ask_legacy(select(LegacyParts))):
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
        session.add(OrderItem(order_id=1, item_id=10, quantity=2))
        session.add(OrderItem(order_id=1, item_id=12, quantity=1))
        session.add(OrderItem(order_id=2, item_id=15, quantity=5))
        session.add(OrderItem(order_id=3, item_id=20, quantity=2))
        session.add(OrderItem(order_id=3, item_id=30, quantity=2))
        session.add(OrderItem(order_id=4, item_id=40, quantity=300))

        session.commit()


def evaluate_missing_costnweight():
    with Session(ENGINE) as session:
        
        # Update the price and weight of each order item if it's missing.
        for a in session.execute(select(OrderItem).where(OrderItem.cost.is_(None))).scalars().all():
            part_weight, part_price = post_scalars(ask_legacy(select(LegacyParts.weight, LegacyParts.price).where(LegacyParts.number == a.item_id)))

            a.cost = part_price * a.quantity
            a.weight = part_weight * a.quantity
        

        session.commit()
    
    print(*full_table(OrderItem), sep="\n")


def update_order_weight():
    # We do all at once because it's then we know it will always be correct
    with Session(ENGINE) as session:
        for a in session.execute(select(Order)).scalars():
            sum_price = 0
            sum_weight = 0
            for b in session.execute(select(OrderItem).where(OrderItem.order_id == a.id)).scalars():
                part_price, part_weight = post_scalars(ask_legacy(select(LegacyParts.price, LegacyParts.weight).where(LegacyParts.number == b.item_id)))
                b.cost = part_price * b.quantity
                b.weight = part_weight * b.quantity
                sum_price += part_price * b.quantity
                sum_weight += part_weight * b.quantity
                # print(b)
            
            a.total_cost = sum_price
            a.total_weight = sum_weight

            fee = session.execute(select(Fees).where(and_(Fees.min_weight <= sum_weight, Fees.max_weight > sum_weight))).scalar()
            if fee:
                # print(fee)
                a.fee_id = fee.id
            # print(a)
        
        session.commit()

            



def main():
    drop_tables()
    build_db()
    update_order_weight()
    # print(*full_table(Order), sep="\n")



if __name__ == '__main__':
    main()
