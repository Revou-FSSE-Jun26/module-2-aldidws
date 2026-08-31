from flask import Blueprint, jsonify, request
from app.controllers import product_controller

product_bp = Blueprint('product', __name__)


@product_bp.route('/products/hardcoded', methods=['GET'])
def get_hardcoded_products():
    """List hardcoded sample products
    ---
    tags:
      - Products
    responses:
      200:
        description: A list of hardcoded products
    """
    result, status = product_controller.get_hardcoded_products()
    return jsonify(result), status


@product_bp.route('/products', methods=['GET'])
def get_all_products():
    """List all products
    ---
    tags:
      - Products
    responses:
      200:
        description: A list of products
    """
    result, status = product_controller.get_all_products()
    return jsonify(result), status


@product_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product
    ---
    tags:
      - Products
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
          properties:
            name:
              type: string
              example: BBS RS 17-inch Alloy Wheels
            price:
              type: integer
              example: 15000000
            stock:
              type: integer
              example: 10
            category_id:
              type: integer
              example: 1
    responses:
      201:
        description: Product created
      400:
        description: Invalid input
    """
    data = request.get_json()
    result, status = product_controller.create_product(data)
    return jsonify(result), status


@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID of the product
    responses:
      200:
        description: The requested product
      404:
        description: Product not found
    """
    result, status = product_controller.get_product(product_id)
    return jsonify(result), status


@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID of the product
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            price:
              type: integer
            stock:
              type: integer
            category_id:
              type: integer
    responses:
      200:
        description: Product updated
      404:
        description: Product not found
    """
    data = request.get_json()
    result, status = product_controller.update_product(product_id, data)
    return jsonify(result), status


@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID of the product
    responses:
      200:
        description: Product deleted
      404:
        description: Product not found
    """
    result, status = product_controller.delete_product(product_id)
    return jsonify(result), status
