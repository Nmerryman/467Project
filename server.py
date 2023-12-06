from flask import Flask, render_template, request, session, redirect, url_for
from legacy_interface import LegacyParts, ask_legacy, post_scalars, get_item_by_id, smart_search
from database_interface import (inventory_from_legacy_id, order_not_done, order_item_not_done, order_update,
                                order_items_from_order, legacy_from_order_item_id, order_from_id, inventory_from_id,
                                inventory_update, customer_new, order_new, order_item_new)
from cc_authorization import authorize_cc
from sqlalchemy import select


app = Flask(__name__)
app.secret_key = 'super secret key'


@app.route("/store_front")
def store_front():
    # get data from legacy database
    # data = ask_legacy(Select(LegacyParts))
    data = get_data_with_inventory()

    # Render the HTML template and pass the data to it
    return render_template('store_front.html', data=data)


@app.route("/")
def default():
    return store_front()


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

    s_res = smart_search(query)

    for item in s_res:
        i_record = inventory_from_legacy_id(item.number)
        if i_record is not None:
            item.stock = i_record.stock

    # Render the HTML template and pass the search results to it
    return render_template('search_results.html', data=s_res)


@app.route('/add_inventory')
def add_inventory():
    data = get_data_with_inventory()
    return render_template('inventory_add.html', data=data)


@app.route('/orders')
def order_menu():
    return render_template('Order_statuses.html', orders=order_not_done(), order_items=all_order_items())



def all_order_items():
    res = {}
    for a in order_item_not_done():
        # Create if missing
        if not a.order_id in res:
            res[a.order_id] = list()
        
        res[a.order_id].append({"name": a.legacy.description, "url": a.legacy.pictureURL, "count": a.quantity})
        
    return res


@app.route("/api/update_order/<val>/<status>")
def update_order(val, status):
    order_update(val, status=status)
    return "ok"


@app.route("/api/add_inventory/<i_id>/<value>")
def increment_inventory(i_id, value):
    print(i_id, value)
    inventory = inventory_from_legacy_id(i_id)
    inventory_update(inventory.id, stock=int(value) + inventory.stock)
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


# further checks need to be done, right now duplicate items are allowed, we want to increment to amount instead
@app.route('/add_to_cart/<item_l_id>/<quantity>', methods=['POST'])
def add_to_cart(item_l_id, quantity):
    if 'cart' not in session:
        session['cart'] = []
    if 'total' not in session:
        session['total'] = 0

    for item in session['cart']:
        if item['id'] == item_l_id:
            item['quantity'] += int(quantity)
            session['total'] += int(quantity)
            session.modified = True
            return 'item already added, added more quantity!!!'
        
    item = {'id': item_l_id, 'quantity': int(quantity)}
    session['cart'].append(item)
    session['total'] += int(quantity)
    session.modified = True
    return 'item successfully added to cart!!!'


@app.route('/cart')
def view_cart():
    # Get the item ids from the session
    item_ids = session.get('cart', [])
    total = session.get('total', 0)
    items = []
    sum_price = 0
    
    for item in item_ids:
        legacy_item = get_item_by_id(item['id'])
        item_details = {'number' : legacy_item.number, 'description': legacy_item.description, 'price': legacy_item.price, 'weight': legacy_item.weight, 'pictureURL': legacy_item.pictureURL, 'quantity': item['quantity']}
        sum_price += legacy_item.price * item['quantity']
        items.append(item_details)

    print(f"Items in cart: {items}")
    print(f"Total items in cart: {total}")

    # TODO Add a fee from weight

    # Pass the items to the template
    return render_template('cart.html', items=items, sum_price=sum_price)


@app.route('/clear_cart')
def clear_cart():
    session.clear()
    return redirect(url_for('store_front'))


@app.route('/get_cart_total', methods=['POST'])
def get_cart_total():
    total = session.get('total', 0)
    return str(total)


@app.route('/checkout')
def checkout():
    # This is just for testing. It holds the url for copy + paste
    test_url = "http://127.0.0.1:5000/cart?name=Dude&email=Dude@email.com&streetAddress=123 street street&city=Cityish&state=North Virginia&zipCode=22222&cardNumber=6011 1234 4321 1234&cardName=Very real&cardExp=1&cardCVV=1&cardZip=1"

    name = request.args.get('arg0')
    email = request.args.get('arg1')
    address = request.args.get('arg2')
    city = request.args.get('arg3')
    state = request.args.get('arg4')
    zip_code = request.args.get('arg5')
    cc_num = request.args.get('arg6')
    cc_name = request.args.get('arg7')
    cc_exp = request.args.get('arg8')
    cc_cvv = request.args.get('arg9')
    cc_zip = request.args.get('arg10')

    # Authorize the card
    result = authorize_cc(cc_num, cc_name, cc_exp, session['total']).json()
    if "errors" in result:
        return render_template('part_card_error.html', errors=result["errors"])

    # We assume the card worked
    customer = customer_new(name, email, address, f"{city}, {state} {zip_code}")
    order = order_new(customer, "In Queue")
    for item in session.get('cart', []):
        legacy = get_item_by_id(item['id'])
        order_item_new(order, legacy, item['quantity'])


    print(session.items())
    print(request.args)
    # print([a for a in request.args.items()])
    return str(result)




