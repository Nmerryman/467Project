from legacy_interface import LegacyParts
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import Select
# for the Legacy database
from database_interface import Inventory, sec
import random
from sqlalchemy import insert

legacy_engine = create_engine("mysql+pymysql://student:student@blitz.cs.niu.edu:3306/csci467", echo=False)
mysql_engine = create_engine("sqlite:///test.db", echo=False)

def add_inventory():
    with Session(legacy_engine) as session:
        # Query to fetch all LegacyParts entries
        query = Select(LegacyParts)
        res = session.execute(query)

        # Iterate over each LegacyParts entry
        for row in res.scalars().all():
            # Generate a random amount of inventory
            random_inventory = random.randint(2, 200)

            # Insert the new inventory into the database
            stmt = insert(Inventory).values(legacy_id=row.number, stock=random_inventory)
            sec(stmt)

    print("Added Inventory")



if __name__ == '__main__':
    #add_inventory()
    

    with Session(legacy_engine) as session:
        # Query to fetch all LegacyParts entries
        query = Select(LegacyParts)
        res = session.execute(query)

        # Iterate over each LegacyParts entry and print the number
        for row in res.scalars().all():
            print(f'Legacy ID: {row.number}')

    print("End of Legacy ID's")

    with Session(mysql_engine) as session:
        # Query to fetch all LegacyParts entries
        query = Select(Inventory)
        res = session.execute(query)

        # Iterate over each LegacyParts entry and print the number
        for row in res.scalars().all():
            print(f'Inventory ID: {row.id}')

    with Session(legacy_engine) as legacy_session, Session(mysql_engine) as mysql_session:
        # Query to fetch all LegacyParts entries
        legacy_query = Select(LegacyParts)
        legacy_res = legacy_session.execute(legacy_query)

        # Query to fetch all Inventory entries
        inventory_query = Select(Inventory)
        inventory_res = mysql_session.execute(inventory_query)

        # Create a dictionary to store the inventory entries
        inventory_dict = {row.legacy_id: row for row in inventory_res.scalars().all()}

        # Iterate over each LegacyParts entry
        for legacy_row in legacy_res.scalars().all():
            # If the part number exists in the inventory dictionary
            if legacy_row.number in inventory_dict:
                # Print the part number and stock id
                print(f'Part Number: {legacy_row.number}, Part Name: {legacy_row.description}, Stock ID: {inventory_dict[legacy_row.number].id}, Stock: {inventory_dict[legacy_row.number].stock}')

    print("End of Legacy ID's")

    test_legacy_id = 1  # replace with a known legacy_id
    inventory_record = ask_inventory(test_legacy_id)
    print(f'Inventory Record for Legacy ID {test_legacy_id}: Legacy ID - {inventory_record.legacy_id}, Stock - {inventory_record.stock}')

    