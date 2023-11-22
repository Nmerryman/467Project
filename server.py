from flask import Flask, render_template
from legacy_interface import LegacyParts, ask_legacy, Select

app = Flask(__name__)

@app.route("/productList")
def productList():
    # Get your data (replace this with your actual data fetching code)
    data = ask_legacy(Select(LegacyParts))

    # Render the HTML template and pass the data to it
    return render_template('productList.html', data=data)

@app.route("/cart")
def cart():
    # Get your cart data (replace this with your actual data fetching code)
    cart_data = ask_legacy(Select(LegacyParts))  # Replace with your cart data fetching code

    # Render the Cart HTML template and pass the cart data to it
    return render_template('cart.html', data=cart_data)

if __name__ == '__main__':
    app.run(debug=True)

    


