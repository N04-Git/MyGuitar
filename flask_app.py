# Libraries
from flask import Flask, render_template, Blueprint, jsonify, send_file
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

@app.route('/tablatures')
def tablatures():
    return render_template("tablatures.html")

@app.route('/classes')
def cours():
    return render_template("cours.html")

# Run (DEV)
if __name__ == "__main__":
    app.run(debug=False, port=8020)