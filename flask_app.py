# Libraries
from flask import Flask, render_template, Blueprint, jsonify
from api import api_router

# App
app = Flask(__name__)

# Register API Routes
app.register_blueprint(api_router)

# Routes
@app.route('/')
def home():
    return render_template("home.html")

# Run
if __name__ == "__main__":
    app.run(debug=False, port=8020)