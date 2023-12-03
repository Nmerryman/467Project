from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from legacy_interface import LegacyParts, ask_legacy, post_scalars, get_item_by_id
from database_interface import (inventory_from_legacy_id, order_not_done, order_item_not_done, order_update,
                                order_items_from_order, legacy_from_order_item_id, order_from_id)
from sqlalchemy import select

import json

app = Flask(__name__)
app.secret_key = 'super secret key'


@app.route("/store_front")
def store_front():
    # get data from legacy database
    # data = ask_legacy(Select(LegacyParts))
    data = get_data_with_inventory()

    # Render the HTML template and pass the data to it
    return render_template('store_front.html', data=data)

@app.route("/search_results")
def search_results():
    # Get your data (replace this with your actual data fetching code)
    data = ask_legacy(Select(LegacyParts))

    # Render the HTML template and pass the data to it
    return render_template('search_results.html', data=data)


@app.route("/search")
def search():
    # Get the search query from the request arguments
    query = request.args.get('arg0') # get key for search term to look up in query

    s_res = perform_search(query)

        # Print the search results to the console
    for item in search_results:
        print(f'Part Number: {item.number}, Part Name: {item.description}, Stock: {item.stock}')

    # Render the HTML template and pass the search results to it
    return render_template('search_results.html', data=s_res)


def perform_search(query):
<<<<<<< Updated upstream
    # Get all data (replace this with your actual data fetching code)
    all_data = ask_legacy(Select(LegacyParts))

    # Filter the data based on the query
    # searches for item in all all_data, and if the item is found within item.description, that item is
    # added to the search results. lower() is to make it case insensitive.
    s_res = list()
    for item in all_data:
        if query.lower() in item.description.lower():
            s_res.append(item)

    # Get inventory data for each search result
    for item in s_res:
        inventory_record = inventory_from_legacy_id(item.number)
        if inventory_record is not None:
            item.stock = inventory_record.stock

    return s_res

@app.route('/add_inventory')
def add_inventory():
    data = get_data_with_inventory()
    return render_template('inventory_add.html', data=data)


@app.route('/orders')
def order_menu():
    return render_template('Order_statuses.html', orders=order_not_done(), order_items=all_order_items())


# @app.route('/api/all_order_items')
def all_order_items():
    res = {}
    for a in order_item_not_done():
        # Create if missing
        if not a.order_id in res:
            res[a.order_id] = list()
        
        res[a.order_id].append({"name": a.legacy.description, "url": a.legacy.pictureURL, "count": a.quantity})
        
    return res


@app.route("/api/update_order/<val>/<status>")
def update_inventory(val, status):
    order_update(val, status=status)
    return "ok"


@app.route("/invoice/<order_id>")
def load_invoice(order_id):
    items = order_items_from_order(order_id)
    order = order_from_id(order_id)
    sum_price = 0
    for a in items:
        a.name = legacy_from_order_item_id(a.id).description
        sum_price += a.cost
    return render_template('invoice.html', order_items=items, order=order, sum_price=sum_price, round=round)


@app.route("/shipping/<order_id>")
def load_shipping(order_id):
    return render_template("shipping.html", order=order_from_id(order_id))


def get_data_with_inventory():
    # Get all data with inventory
    all_data = post_scalars(ask_legacy(select(LegacyParts)))

    # a legacy part, s is a number, which is the stock
    return [{"l": a, "s": inventory_from_legacy_id(a.number).stock} for a in all_data]
    
from flask import request, jsonify

# further checks need to be done, right now duplicate items are allowed, we want to increment to amount instead
@app.route('/add_to_cart/<item_id>', methods=['POST'])
def add_to_cart(item_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(item_id)
    session.modified = True
    return 'item successfully added to cart!!!'

@app.route('/cart')
def view_cart():
    # Get the item ids from the session
    item_ids = session.get('cart', [])
    items = []
    
    for item_id in item_ids:
        item = get_item_by_id(item_id)
        items.append(item)

    print(f"Items in cart: {items}")

    # Pass the items to the template
    return render_template('cart.html', items=items)

@app.route('/clear_cart')
def clear_cart():
    session.clear()
    return redirect(url_for('store_front'))


