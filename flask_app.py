# Libraries
from flask import Flask, render_template, Blueprint, jsonify, send_from_directory
from api import api_router

# App
app = Flask(__name__)

# Register API Routes
app.register_blueprint(api_router)

# Routes
@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/key')
def key():
    return render_template("gamme.html")

@app.route('/chords')
def chords():
    return render_template("accords.html")

@app.route('/practice')
def practice():
    return render_template("exercises.html")

# Run
if __name__ == "__main__":
    app.run(debug=False, port=8020)