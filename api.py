# API Routes
from flask import Blueprint, jsonify

api_router = Blueprint('api', __name__, url_prefix='/api')

@api_router.route('/')
def api():
    return jsonify({"api":"ok"})

