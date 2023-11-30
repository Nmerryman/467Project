from flask import Flask, render_template, request
from legacy_interface import LegacyParts, ask_legacy, post_scalars
from database_interface import inventory_from_legacy_id
from sqlalchemy import select

app = Flask(__name__)


@app.route("/store_front")
def productList():
    # get data from legacy database
    # data = ask_legacy(Select(LegacyParts))
    data = get_data_with_inventory()

    # Render the HTML template and pass the data to it
    return render_template('store_front.html', data=data)

@app.route("/")
def default():
    return productList()


@app.route("/search_results")
def search_results():
    # Get your data (replace this with your actual data fetching code)
    data = ask_legacy(select(LegacyParts))

    # Render the HTML template and pass the data to it
    return render_template('search_results.html', data=data)


@app.route("/search")
def search():
    # Get the search query from the request arguments
    query = request.args.get('arg0') # get key for search term to look up in query

    search_results = perform_search(query)

        # Print the search results to the console
    for item in search_results:
        print(f'Part Number: {item.number}, Part Name: {item.description}, Stock: {item.stock}')

    # Render the HTML template and pass the search results to it
    return render_template('search_results.html', data=search_results)


def perform_search(query):
    # Get all data (replace this with your actual data fetching code)
    all_data = ask_legacy(select(LegacyParts))

    # Filter the data based on the query
    # searches for item in all all_data, and if the item is found within item.description, that item is
    # added to the search results. lower() is to make it case insensitive.
    search_results = [item for item in all_data if query.lower() in item.description.lower()]

    # Get inventory data for each search result
    for item in search_results:
        inventory_record = inventory_from_legacy_id(item.number)
        if inventory_record is not None:
            item.stock = inventory_record.stock

    return search_results


@app.route('/cart')
def cart_elements():
    data = ask_legacy(select(LegacyParts))
    return render_template('cart.html', data=data)


def get_data_with_inventory():
    # Get all data (replace this with your actual data fetching code)
    all_data = post_scalars(ask_legacy(select(LegacyParts)))

    return [{"l": a, "s": inventory_from_legacy_id(a.number).stock} for a in all_data]


    


