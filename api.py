# API Routes
from flask import Blueprint, jsonify, request
import guitar

api_router = Blueprint('api', __name__, url_prefix='/api')

@api_router.route('/')
def api():
    return jsonify("Welcome To MyGuitar's API !")

@api_router.route('/key', methods=['POST'])
def key():

    # Check input
    data = request.get_json()
    try:
        mode_name = data['mode']
        key_name = data['key']
        if not mode_name and key_name:
            return jsonify("Error: empty argument(s)")

        k = guitar.get_key(mode_name, key_name)
        if k:
            return jsonify(k)

        return jsonify('Error: key not found')

    except KeyError:
        return jsonify("Error: missing argument(s)")

@api_router.route('/chart', methods=['POST'])
def chart():

    data = request.get_json()
    try:
        chord_id = data['chord_id']
        chart = guitar.get_chart(chord_id)

        if chart:
            return jsonify(chart)

    except KeyError:
        return jsonify("Error: missing argument(s)")

    return jsonify('API Error: Chart not found')