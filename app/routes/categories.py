from flask import Blueprint, jsonify, request
from app.models import Category, Product
from app import db

category_bp = Blueprint('category', __name__)


#--- Create a new category
@category_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({"error": "Missing required field: name"}), 400

    new_category = Category(
        name=data['name'],
        description=data.get('description')
    )

    db.session.add(new_category)
    db.session.commit()

    return jsonify(new_category.to_dict()), 201


#--- List all categories
@category_bp.route('/categories', methods=['GET'])
def get_all_categories():
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories]), 200


#--- Get a specific category
@category_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    category_data = category.to_dict()
    category_data['products'] = [product.to_dict() for product in category.products]

    return jsonify(category_data), 200


#--- Update category
@category_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "The data request is invalid or empty."}), 400

    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']

    try:
        db.session.commit()
        return jsonify({
            "message": "Category successfully updated",
            "category": category.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update category: {str(e)}"}), 500


#--- Delete category
@category_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": f"Category '{category.name}' successfully deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete category: {str(e)}"}), 500
