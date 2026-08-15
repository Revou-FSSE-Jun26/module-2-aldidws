from flask import Blueprint, jsonify
from app.models import Product

product_bp = Blueprint('product', __name__)


@product_bp.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200


@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify(product.to_dict()), 200
    return jsonify({"error": "Product not found"}), 404
