from app import db
from app.models import Product

HARDCODED_PRODUCTS = [
    {"id": 1, "name": "BBS RS 17-inch Alloy Wheels", "price": 15000000, "stock": 10, "category": "Wheels and Tires"},
    {"id": 2, "name": "Volk Rays TE37 18-inch Forged Wheels", "price": 25000000, "stock": 5, "category": "Wheels and Tires"},
    {"id": 3, "name": "Stainless Steel Catback Exhaust for E36", "price": 5500000, "stock": 8, "category": "Performance Exhaust"},
    {"id": 4, "name": "High-Performance 10W-40 Synthetic Oil 1L", "price": 150000, "stock": 100, "category": "Engine Maintenance"},
    {"id": 5, "name": "Premium Power Steering Fluid", "price": 120000, "stock": 50, "category": "Engine Maintenance"},
]


def get_hardcoded_products():
    """Return static hardcoded product list."""
    return HARDCODED_PRODUCTS, 200


def get_all_products():
    """Retrieve all products from database."""
    products = Product.query.all()
    return [product.to_dict() for product in products], 200


def get_product(product_id):
    """Retrieve a single product by ID."""
    product = db.session.get(Product, product_id)
    if product:
        return product.to_dict(), 200
    return {"error": "Product not found"}, 404


def create_product(data):
    """Create a new product."""
    if not data or not data.get('name') or not data.get('price') or not data.get('stock'):
        return {"error": "Missing required fields: name, price, stock"}, 400

    new_product = Product(
        name=data['name'],
        price=data['price'],
        stock=data['stock'],
        category_id=data.get('category_id')
    )

    db.session.add(new_product)
    db.session.commit()

    return new_product.to_dict(), 201


def update_product(product_id, data):
    """Update an existing product."""
    product = db.session.get(Product, product_id)

    if not product:
        return {"error": "Product not found"}, 404

    if not data:
        return {"error": "The data request is invalid or empty."}, 400

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
        return {"message": "Product successfully updated", "product": product.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to update product: {str(e)}"}, 500


def delete_product(product_id):
    """Delete a product if no orders are linked."""
    product = db.session.get(Product, product_id)

    if not product:
        return {"error": "Product not found"}, 404

    from app.models.order_item import order_items
    linked_orders = db.session.execute(
        order_items.select().where(order_items.c.product_id == product_id)
    ).fetchone()

    if linked_orders:
        return {"error": "Cannot delete product with existing orders."}, 400

    try:
        db.session.delete(product)
        db.session.commit()
        return {"message": f"Product '{product.name}' successfully deleted"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to delete product: {str(e)}"}, 500
