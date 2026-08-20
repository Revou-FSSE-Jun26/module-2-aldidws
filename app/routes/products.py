from flask import Blueprint, jsonify, request
from app.models import Product
from app import db

product_bp = Blueprint('product', __name__)

HARDCODED_PRODUCTS = [
    {"id": 1, "name": "BBS RS 17-inch Alloy Wheels", "price": 15000000, "stock": 10, "category": "Wheels and Tires"},
    {"id": 2, "name": "Volk Rays TE37 18-inch Forged Wheels", "price": 25000000, "stock": 5, "category": "Wheels and Tires"},
    {"id": 3, "name": "Stainless Steel Catback Exhaust for E36", "price": 5500000, "stock": 8, "category": "Performance Exhaust"},
    {"id": 4, "name": "High-Performance 10W-40 Synthetic Oil 1L", "price": 150000, "stock": 100, "category": "Engine Maintenance"},
    {"id": 5, "name": "Premium Power Steering Fluid", "price": 120000, "stock": 50, "category": "Engine Maintenance"},
]


@product_bp.route('/products/hardcoded', methods=['GET'])
def get_hardcoded_products():
    return jsonify(HARDCODED_PRODUCTS), 200

#--- Get all product
@product_bp.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200

#--- Create new product
@product_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()

    if not data or not data.get('name') or not data.get('price') or not data.get('stock'):
        return jsonify({"error": "Missing required fields: name, price, stock"}), 400

    new_product = Product(
        name=data['name'],
        price=data['price'],
        stock=data['stock'],
        category_id=data.get('category_id')
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify(new_product.to_dict()), 201

#--- Get a specific product
@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify(product.to_dict()), 200
    return jsonify({"error": "Product not found"}), 404

#--- Update a product
@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "The data request is invalid or empty."}), 400

    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'stock' in data:
        product.stock = data['stock']
    if 'category_id' in data:
        product.category_id = data['category_id']

    try:
        db.session.commit()
        return jsonify({
            "message": "Product successfully updated",
            "product": product.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update product: {str(e)}"}), 500


#--- Delete a product
@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f"Product '{product.name}' successfully deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete product: {str(e)}"}), 500

