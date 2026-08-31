from flask import Blueprint, jsonify, request
from app.controllers import category_controller

category_bp = Blueprint('category', __name__)


@category_bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new category
    ---
    tags:
      - Categories
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: Wheels and Tires
    responses:
      201:
        description: Category created
      400:
        description: Invalid input
    """
    data = request.get_json()
    result, status = category_controller.create_category(data)
    return jsonify(result), status


@category_bp.route('/categories', methods=['GET'])
def get_all_categories():
    """List all categories
    ---
    tags:
      - Categories
    responses:
      200:
        description: A list of categories
    """
    result, status = category_controller.get_all_categories()
    return jsonify(result), status


@category_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get a single category by ID
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
        description: ID of the category
    responses:
      200:
        description: The requested category
      404:
        description: Category not found
    """
    result, status = category_controller.get_category(category_id)
    return jsonify(result), status


@category_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update an existing category
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
        description: ID of the category
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
    responses:
      200:
        description: Category updated
      404:
        description: Category not found
    """
    data = request.get_json()
    result, status = category_controller.update_category(category_id, data)
    return jsonify(result), status


@category_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
        description: ID of the category
    responses:
      200:
        description: Category deleted
      404:
        description: Category not found
    """
    result, status = category_controller.delete_category(category_id)
    return jsonify(result), status
