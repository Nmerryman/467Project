import faker
import random
from legacy_interface import ask_legacy, LegacyParts
from database_interface import *

from sqlalchemy import Select

fake = faker.Faker()

gen_counts = {"Customers": 50, "Fees": 3, "Inventory": 50, "OrderItem": 100, "Order": 10}
status_options = ["pre", "in", "post"]


def test_legacy():
    """
    Testing to make sure that we can connect to the legacy database and get valid results
    """
    query = Select(LegacyParts).filter(LegacyParts.price > 100)
    res = ask_legacy(query)
    assert len(res) > 10, res

    query = Select(LegacyParts).filter(LegacyParts.price < 100)
    res = ask_legacy(query)
    assert len(res) > 10, res

    query = Select(LegacyParts).filter(LegacyParts.price > 10000)
    res = ask_legacy(query)
    assert len(res) == 0, res

    print("Passed Legacy test")


def drop_tables():
    """
    Drop all tables
    """
    Base.metadata.drop_all(ENGINE)


def make_tables():
    """
    Make sure all tables exist
    """
    Base.metadata.create_all(ENGINE)


def add_customer():
    with Session(ENGINE) as session:
        for _ in range(gen_counts["Customers"]):
            address = fake.address().split("\n")
            customer = Customer(name=fake.name(), email=fake.email(), address1=address[0], address2=address[1])
            session.add(customer)
            # session.flush()  # This is good if I want to be able to see the id after changes
            # print(customer.id)
        session.commit()

    print("Added Customers")


def add_fees():
    Base.metadata.drop_all(ENGINE, tables=[Fees.__table__])
    Base.metadata.create_all(ENGINE)

    size = 50
    start = 0
    after = random.random() * size
    with Session(ENGINE) as session:
        for _ in range(gen_counts["Fees"]):
            f = Fees(name=fake.text()[0:100], weight_m=random.random()*50, weight_b=random.random()*50, min_weight=start, max_weight=after)
            session.add(f)

            start = after
            after += random.random() * size
            
        session.commit()

    print("Added Fees")


def add_inventory():
    Base.metadata.drop_all(ENGINE, tables=[Inventory.__table__])
    Base.metadata.create_all(ENGINE)

    with Session(ENGINE) as session:
        for _ in range(gen_counts["Inventory"]):
            inv = Inventory(legacy_id=random.randint(1, 100), stock=random.randint(2, 200))
            session.add(inv)
        session.commit()

    print("Added Inventory")


def add_order():
    Base.metadata.drop_all(ENGINE, tables=[Order.__table__])
    Base.metadata.create_all(ENGINE)

    with Session(ENGINE) as sesison:
        for _ in range(gen_counts["Order"]):
            finished_date = fake.date_time_between(start_date="now", end_date="+1y") if random.random() > 0.5 else None
            order = Order(customer_id=random.randint(1, gen_counts["Customers"]), status=random.choice(status_options),
                                        created=fake.date_time_between(start_date="-1y", end_date="now"), finished=finished_date,
                                        fee_id=random.randint(1, gen_counts["Fees"]), total_cost=random.random() * 20_000)
            sesison.add(order)
        sesison.commit()

    print("Added Order")


def add_order_item():
    Base.metadata.drop_all(ENGINE, tables=[OrderItem.__table__])
    Base.metadata.create_all(ENGINE)

    with Session(ENGINE) as session:
        for _ in range(gen_counts["OrderItem"]):
            oi = OrderItem(order_id=random.randint(1, gen_counts["Order"]), item_id=random.randint(1, gen_counts["Inventory"]),
                                            quantity=random.randint(1, 20), status=random.choice(status_options),
                                            cost=random.random()*50)
            session.add(oi)
        session.commit()

    print("Added OrderItems")


def gen_tables():
    # Just do all at once in order
    drop_tables()
    make_tables()
    add_customer()
    add_fees()
    add_inventory()
    add_order()
    add_order_item()


if __name__ == '__main__':
    gen_tables()
