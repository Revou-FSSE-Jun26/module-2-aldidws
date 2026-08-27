from flask import Blueprint, jsonify, request
from app.controllers import category_controller

category_bp = Blueprint('category', __name__)


@category_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    result, status = category_controller.create_category(data)
    return jsonify(result), status


@category_bp.route('/categories', methods=['GET'])
def get_all_categories():
    result, status = category_controller.get_all_categories()
    return jsonify(result), status


@category_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    result, status = category_controller.get_category(category_id)
    return jsonify(result), status


@category_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.get_json()
    result, status = category_controller.update_category(category_id, data)
    return jsonify(result), status


@category_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    result, status = category_controller.delete_category(category_id)
    return jsonify(result), status
