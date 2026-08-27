from app import db
from app.models import Category


def get_all_categories():
    """Retrieve all categories."""
    categories = Category.query.all()
    return [category.to_dict() for category in categories], 200


def get_category(category_id):
    """Retrieve a single category with its products."""
    category = db.session.get(Category, category_id)

    if not category:
        return {"error": "Category not found"}, 404

    category_data = category.to_dict()
    category_data['products'] = [product.to_dict() for product in category.products]

    return category_data, 200


def create_category(data):
    """Create a new category."""
    if not data or not data.get('name'):
        return {"error": "Missing required field: name"}, 400

    new_category = Category(
        name=data['name'],
        description=data.get('description')
    )

    db.session.add(new_category)
    db.session.commit()

    return new_category.to_dict(), 201


def update_category(category_id, data):
    """Update an existing category."""
    category = db.session.get(Category, category_id)

    if not category:
        return {"error": "Category not found"}, 404

    if not data:
        return {"error": "The data request is invalid or empty."}, 400

    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']

    try:
        db.session.commit()
        return {"message": "Category successfully updated", "category": category.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to update category: {str(e)}"}, 500


def delete_category(category_id):
    """Delete a category."""
    category = db.session.get(Category, category_id)

    if not category:
        return {"error": "Category not found"}, 404

    try:
        db.session.delete(category)
        db.session.commit()
        return {"message": f"Category '{category.name}' successfully deleted"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to delete category: {str(e)}"}, 500
