# API Routes
from flask import Blueprint, jsonify, request, send_file
import guitar, exercises # type: ignore

api_router = Blueprint('api', __name__, url_prefix='/api')

ERROR_MISSING_ARGS = ('Error: missing argument(s)')


@api_router.route('/')
def api():
    return jsonify("Welcome To MyGuitar's API ! >> https://myportfolio.ackernoa.fr <<")

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
        return jsonify(ERROR_MISSING_ARGS)

@api_router.route('/chart', methods=['POST'])
def chart():

    data = request.get_json()
    try:
        chord_id = data['chord_id']
        chart = guitar.get_chart(chord_id)

        if chart:
            return jsonify(chart)

    except KeyError:
        return jsonify(ERROR_MISSING_ARGS)

    return jsonify('API Error: Chart not found')

@api_router.route('/exercises', methods=['POST'])
def exercises():

    data = request.get_json()
    try:
        exercise_prefix = data['name']
        exercise_category = data['category']
        exercise_sort = data['sort']

        e = guitar.get_exercies(exercise_category, exercise_sort, exercise_prefix)

        return jsonify(e)

    except KeyError:
        return jsonify(ERROR_MISSING_ARGS)

@api_router.route('/gpfile/<fname>')
def get_gpfile(fname:str):
    return send_file(f'gpfile\\{fname}')

@api_router.route('/chords', methods=['POST'])
def get_chords():

    data = request.get_json()
    try:
        # Param
        chord_prefix = data['prefix']
        chord_kind = data['kind']

        # Get chords from param
        found_chords = guitar.get_chords(chord_prefix, chord_kind)

        # Return
        return jsonify(found_chords)
    except KeyError:
        return jsonify(ERROR_MISSING_ARGS)

@api_router.route('/fretboard', methods=['POST'])
def get_fretboard():
    data = request.get_json()
    try:
        # Param
        chord_id = data['chord_id']
        return jsonify(guitar.get_chord_fretboard(chord_id))

    except KeyError:
        return jsonify(ERROR_MISSING_ARGS)
