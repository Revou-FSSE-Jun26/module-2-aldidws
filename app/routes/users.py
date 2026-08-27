from flask import Blueprint, jsonify, request
from app.controllers import user_controller

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['GET'])
def get_all_users():
    result, status = user_controller.get_all_users()
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    result, status = user_controller.get_single_user(user_id)
    return jsonify(result), status


@user_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json(silent=True) or {}
    result, status = user_controller.register_user(data)
    return jsonify(result), status


@user_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    result, status = user_controller.login(data)
    return jsonify(result), status
