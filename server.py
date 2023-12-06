from flask import Flask, render_template, request, session, redirect, url_for
from legacy_interface import LegacyParts, ask_legacy, post_scalars, get_legacy_item_by_id, smart_search
from database_interface import (inventory_from_legacy_id, order_not_done, order_item_not_done, order_update,
                                order_items_from_order, legacy_from_order_item_id, order_from_id, inventory_from_id,
                                inventory_update, customer_new, order_new, order_item_new, fee_from_all, fee_delete,
                                fee_new, update_order_weight, fee_from_weight, order_all, search_orders_by_date,
                                search_orders)
from cc_authorization import authorize_cc
from sqlalchemy import select


app = Flask(__name__)
app.secret_key = 'super secret key'


@app.route("/")
def default():
    return store_front()


@app.route("/store_front")
def store_front():
    # get data from legacy database
    # data = ask_legacy(Select(LegacyParts))
    data = get_data_with_inventory()

    # Render the HTML template and pass the data to it
    return render_template('store_front.html', data=data)


@app.route("/search")
def search():
    # Get the search query from the request arguments
    query = request.args.get('arg0') # get key for search term to look up in query

    s_res = smart_search(query)

    res = []
    for item in s_res:
        temp = {'l': item, 's': inventory_from_legacy_id(item.number).stock}
        res.append(temp)

    # Render the HTML template and pass the search results to it
    return render_template('search_results.html', data=res)


@app.route('/add_inventory')
def add_inventory():
    data = get_data_with_inventory()
    return render_template('inventory_add.html', data=data)


@app.route('/search_inventory')
def search_inventory():
    query = request.args.get('arg0')
    s_res = smart_search(query)

    res = []
    for item in s_res:
        temp = {'l': item, 's': inventory_from_legacy_id(item.number).stock}
        res.append(temp)

    return render_template('inventory_search.html', data=res)


def get_data_with_inventory():
    # Get all data with inventory
    all_data = post_scalars(ask_legacy(select(LegacyParts)))

    # a legacy part, s is a number, which is the stock
    return [{"l": a, "s": inventory_from_legacy_id(a.number).stock} for a in all_data]


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


@app.route('/remove_from_cart/<item_l_id>')
def remove_from_cart(item_l_id):
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == item_l_id:
            cart.remove(item)
            session['total'] -= item['quantity']
            return "ok"



@app.route('/cart')
def view_cart():
    # Get the item ids from the session
    total = session.get('total', 0)
    sum_price = 0

    # sum_price += legacy_item.price * item['quantity']

    # print(f"Items in cart: {items}")
    # print(f"Total items in cart: {total}")

    # TODO Add a fee from weight

    # Pass the items to the template
    return render_template('cart.html', sum_price=sum_price)


@app.route('/get_cart_items')
def get_cart_items():
    item_ids = session.get('cart', [])
    items = []

    for item in item_ids:
        legacy_item = get_legacy_item_by_id(item['id'])
        item_details = {'number' : legacy_item.number, 'description': legacy_item.description, 'price': legacy_item.price, 'weight': legacy_item.weight, 'pictureURL': legacy_item.pictureURL, 'quantity': item['quantity']}
        items.append(item_details)

    return render_template('part_cart_item.html', items=items)


@app.route('/get_cart_stats')
def get_cart_stats():
    sum_weight = 0
    sum_price = 0
    for item in session.get('cart', []):
        legacy_item = get_legacy_item_by_id(item['id'])
        sum_weight += legacy_item.weight * item['quantity']
        sum_price += legacy_item.price * item['quantity']
    fee = fee_from_weight(sum_weight)
    sum_fee = fee.weight_m * sum_weight + fee.weight_b
    sum_total = sum_price + sum_fee


    return render_template('part_cart_stats.html', price=sum_price, weight=sum_weight, fees=sum_fee, total=sum_total, round=round)

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

    # Make sure that there are items in the cart
    if session.get('total', 0) <= 0:
        return render_template('part_card_error.html', errors=["No items in cart"])

    # Authorize the card
    result = authorize_cc(cc_num, cc_name, cc_exp, session['total']).json()
    if "errors" in result:
        return render_template('part_card_error.html', errors=result["errors"])

    # We assume the card worked
    customer = customer_new(name, email, address, f"{city}, {state} {zip_code}")
    order_id = order_new(customer, "IN CART")
    print(session.items())
    print(request.args)
    for item in session.get('cart', []):
        inv = inventory_from_legacy_id(item['id'])
        order_item_new(order_id, inv.id, item['quantity'])
        inv.stock -= item['quantity']

    update_order_weight()
    session.clear()


    # print([a for a in request.args.items()])
    return render_template("thank_you.html", order_num=order_id, trans=result["trans"], order_id=result["_id"], name=name, email=email, street_address=address, city=city, state=state, zip_code=zip_code)


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/admin/history')
def admin_history():
    return render_template('admin_history.html')

@app.route('/admin/brackets')
def admin_brackets():

    return render_template('admin_brackets.html')

@app.route('/api/load_brackets')
def load_brackets():
    return render_template("part_admin_brackets.html", items=fee_from_all())


@app.route('/api/remove_bracket/<f_id>')
def remove_bracket(f_id):
    fee_delete(f_id)
    return "ok"

@app.route('/api/add_bracket')
def add_bracket():
    res = [a for a in request.args.values()]
    if all(res):
        fee_new(*res)
    return "ok"


@app.route('/directory')
def directory():
    return render_template('directory.html')


@app.route('/api/load_orders')
def load_orders():
    return render_template("part_admin_orders.html", orders=order_all())


def get_data_with_inventory():
    # Get all data with inventory
    all_data = post_scalars(ask_legacy(select(LegacyParts)))

    # a legacy part, s is a number, which is the stock
    return [{"l": a, "s": inventory_from_legacy_id(a.number).stock} for a in all_data]

@app.route("/date_search", methods=['GET'])
def date_search():
    # Get the start and end dates from the request arguments
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Use the search_orders_by_date function to get the orders
    orders = search_orders_by_date(start_date_str, end_date_str)

    # Render the HTML template and pass the filtered orders to it
    return render_template('search_results.html', orders=orders)

@app.route("/record_search", methods=['GET'])
def record_search():
    # Get the parameters from the request arguments
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    min_cost = request.args.get('min_cost')
    max_cost = request.args.get('max_cost')

    # If min_cost or max_cost is not provided or is an empty string, set them to None
    min_cost = float(min_cost) if min_cost and min_cost != 'null' else None
    max_cost = float(max_cost) if max_cost and max_cost != 'null' else None
    # print(min_cost, max_cost)

    # Use the search_orders function to get the orders
    orders = search_orders(start_date, end_date, status, min_cost, max_cost)
    print(orders)

    temp = []
    for a in orders:
        a.invoice_html = load_invoice(a.id)
        a.shipping_html = load_shipping(a.id)

    # Render the HTML template and pass the filtered orders to it
    return render_template('part_admin_orders.html', orders=orders)




