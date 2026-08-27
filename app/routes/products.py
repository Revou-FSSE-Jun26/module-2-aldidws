from flask import Blueprint, jsonify, request
from app.controllers import product_controller

product_bp = Blueprint('product', __name__)


@product_bp.route('/products/hardcoded', methods=['GET'])
def get_hardcoded_products():
    result, status = product_controller.get_hardcoded_products()
    return jsonify(result), status


@product_bp.route('/products', methods=['GET'])
def get_all_products():
    result, status = product_controller.get_all_products()
    return jsonify(result), status


@product_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    result, status = product_controller.create_product(data)
    return jsonify(result), status


@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    result, status = product_controller.get_product(product_id)
    return jsonify(result), status


@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    result, status = product_controller.update_product(product_id, data)
    return jsonify(result), status


@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    result, status = product_controller.delete_product(product_id)
    return jsonify(result), status
