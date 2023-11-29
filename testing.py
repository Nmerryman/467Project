import faker
import random
from legacy_interface import ask_legacy, LegacyParts
from database_interface import *

from sqlalchemy import Select

fake = faker.Faker()

gen_counts = {"Customers": 50, "FeeBrackets": 4, "Fees": 30, "Inventory": 50, "OrderItem": 100, "Order": 10}
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
    for _ in range(gen_counts["Customers"]):
        address = fake.address().split('\n')
        stmt = insert(Customer).values(name=fake.name(), email=fake.email(), address1=address[0], address2=address[1])
        sec(stmt)
    print("Added Customers")


def add_fee_bracket():
    # Clear the table because we don't really want to randomly generate extra rows
    Base.metadata.drop_all(ENGINE, tables=[FeeBrackets.__table__])
    Base.metadata.create_all(ENGINE)

    steps = gen_counts["FeeBrackets"]
    size = 50
    start = 0
    after = random.random() * size

    for a in range(steps):
        stmt = insert(FeeBrackets).values(name=f"Step: {a}", min_weight=start, max_weight=after)
        sec(stmt)

        start = after
        after = random.random() * size

    print("Added FeeBrackets")


def add_fees():
    Base.metadata.drop_all(ENGINE, tables=[Fees.__table__])
    Base.metadata.create_all(ENGINE)

    for _ in range(gen_counts["Fees"]):
        stmt = insert(Fees).values(description=fake.text()[0:100], bracket=random.randint(1, gen_counts["FeeBrackets"]),
                                   base_charge=random.random()*500, weight_m=random.random()*50,
                                   weight_b=random.random()*50)
        sec(stmt)

    print("Added Fees")


def add_inventory():
    Base.metadata.drop_all(ENGINE, tables=[Inventory.__table__])
    Base.metadata.create_all(ENGINE)

    for _ in range(gen_counts["Inventory"]):
        stmt = insert(Inventory).values(legacy_id=random.randint(1, 100), stock=random.randint(2, 200))
        sec(stmt)

    print("Added Inventory")

def add_order():
    Base.metadata.drop_all(ENGINE, tables=[Order.__table__])
    Base.metadata.create_all(ENGINE)

    for _ in range(gen_counts["Order"]):
        finished_date = fake.date_time_between(start_date="now", end_date="+1y") if random.random() > 0.5 else None
        stmt = insert(Order).values(customer_id=random.randint(1, gen_counts["Customers"]), status=random.choice(status_options),
                                    created=fake.date_time_between(start_date="-1y", end_date="now"), finished=finished_date,
                                    pricing_model_id=random.randint(1, gen_counts["Fees"]), calculated_cost=random.random() * 20_000)
        sec(stmt)

    print("Added Order")


def add_order_item():
    Base.metadata.drop_all(ENGINE, tables=[OrderItem.__table__])
    Base.metadata.create_all(ENGINE)

    for _ in range(gen_counts["OrderItem"]):
        stmt = insert(OrderItem).values(order_id=random.randint(1, gen_counts["Order"]), item_id=random.randint(1, gen_counts["Inventory"]),
                                        quantity=random.randint(1, 20), status=random.choice(status_options),
                                        cost=random.random()*50)
        sec(stmt)

    print("Added OrderItems")

def get_combined_data():
    # Create a new session
    with Session(ENGINE) as session:
        # Perform a join operation between Inventory and LegacyParts
        # Replace 'LegacyParts' with the actual name of your LegacyParts class
        # Replace 'legacy_id' and 'id' with the actual names of your foreign key and primary key
        data = session.query(Inventory, LegacyParts).join(LegacyParts, Inventory.legacy_id == LegacyParts.number).all()
        print(str(session.query(Inventory, LegacyParts).join(LegacyParts, Inventory.legacy_id == LegacyParts.number)))
        # Close the session
        session.close()

    return data



def gen_tables():
    # Just do all at once in order
    drop_tables()
    make_tables()
    add_customer()
    add_fee_bracket()
    add_fees()
    add_inventory()
    add_order()
    add_order_item()



if __name__ == '__main__':
    #gen_tables()
    drop_tables()
    make_tables()
