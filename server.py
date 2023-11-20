from flask import Flask, render_template
from legacy_interface import LegacyParts, ask_legacy, Select

app = Flask(__name__)

@app.route("/")
def default():
    # Get your data (replace this with your actual data fetching code)
    data = ask_legacy(Select(LegacyParts).filter(LegacyParts.price >= 100))

    # Render the HTML template and pass the data to it
    return render_template('index.html', data=data)

    


