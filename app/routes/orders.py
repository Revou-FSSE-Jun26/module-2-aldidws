from flask import Blueprint, jsonify, request
from app.middleware.auth import token_required, owner_required
from app.controllers import order_controller

order_bp = Blueprint('order', __name__)


@order_bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json()
    result, status = order_controller.create_order(current_user, data)
    return jsonify(result), status


@order_bp.route('/orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    result, status = order_controller.get_user_orders(current_user)
    return jsonify(result), status


@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    result, status = order_controller.get_order(current_user, order_id)
    return jsonify(result), status


@order_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@token_required
@owner_required
def delete_order(current_user, order_id):
    result, status = order_controller.delete_order(current_user, order_id)
    return jsonify(result), status
