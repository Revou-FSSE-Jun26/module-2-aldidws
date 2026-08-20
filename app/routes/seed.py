from flask import Blueprint, jsonify
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Product, Category, Order, order_items

seed_bp = Blueprint('seed', __name__)


@seed_bp.route('/seed/users', methods=['POST'])
def seed_users():
    if User.query.count() == 0:
        sample_users = [
            User(username='Abdul Hafidz', email='Abdul@example.com', password_hash=generate_password_hash('hashed_pw_123')),
            User(username='Nadas Kahfi', email='Nadas@example.com', password_hash=generate_password_hash('hashed_pw_456')),
            User(username='Hanif Adhi', email='Hanif@example.com', password_hash=generate_password_hash('hashed_pw_789')),
        ]
        db.session.add_all(sample_users)
        db.session.commit()
        return jsonify({"message": "Seeded 3 users successfully"}), 201
    return jsonify({"message": "Users already exist"}), 400


@seed_bp.route('/seed/products', methods=['POST'])
def seed_products():
    categories = Category.query.order_by(Category.id).all()
    if len(categories) < 3:
        return jsonify({"error": "You must seed the categories first!"}), 400

    if Product.query.count() == 0:
        wheels = categories[0].id
        exhaust = categories[1].id
        engine = categories[2].id

        sample_products = [
            Product(name="BBS RS 17-inch Alloy Wheels", price=15000000, stock=10, category_id=wheels),
            Product(name="Volk Rays TE37 18-inch Forged Wheels", price=25000000, stock=5, category_id=wheels),
            Product(name="Stainless Steel Catback Exhaust for E36", price=5500000, stock=8, category_id=exhaust),
            Product(name="High-Performance 10W-40 Synthetic Oil 1L", price=150000, stock=100, category_id=engine),
            Product(name="Premium Power Steering Fluid", price=120000, stock=50, category_id=engine),
        ]
        db.session.add_all(sample_products)
        db.session.commit()
        return jsonify({"message": "Seeded 5 products successfully"}), 201
    return jsonify({"message": "Products already exist"}), 400


@seed_bp.route('/seed/categories', methods=['POST'])
def seed_categories():
    if Category.query.count() == 0:
        sample_categories = [
            Category(name='Wheels and Tires'),
            Category(name='Performance Exhaust'),
            Category(name='Engine Maintenance'),
        ]
        db.session.add_all(sample_categories)
        db.session.commit()
        return jsonify({"message": "Seeded 3 categories successfully"}), 201
    return jsonify({"message": "Categories already exist"}), 400


@seed_bp.route('/seed/orders', methods=['POST'])
def seed_orders():
    users = User.query.order_by(User.id).all()
    products = Product.query.order_by(Product.id).all()

    if len(users) < 2 or len(products) < 4:
        return jsonify({"error": "Harus melakukan seed users dan products terlebih dahulu!"}), 400

    # Check if order_items already has data
    count = db.session.execute(db.select(db.func.count()).select_from(order_items)).scalar()
    if count == 0:
        sample_orders = [
            Order(user_id=users[0].id, total_amount=25000000, status='pending'),
            Order(user_id=users[1].id, total_amount=5650000, status='pending'),
        ]
        db.session.add_all(sample_orders)
        db.session.commit()

        # Insert into order_items association table
        db.session.execute(order_items.insert().values([
            {"order_id": sample_orders[0].id, "product_id": products[1].id, "quantity": 1, "price": 25000000},
            {"order_id": sample_orders[1].id, "product_id": products[2].id, "quantity": 1, "price": 5500000},
            {"order_id": sample_orders[1].id, "product_id": products[3].id, "quantity": 2, "price": 150000},
        ]))
        db.session.commit()
        return jsonify({"message": "Seeded 2 orders with 3 order items successfully"}), 201
    return jsonify({"message": "Order items already exist"}), 400


@seed_bp.route('/clear', methods=['POST'])
def clear():
    try:
        db.session.execute(order_items.delete())
        Order.query.delete()
        Product.query.delete()
        Category.query.delete()
        User.query.delete()
        db.session.commit()

        # Reset sequences so IDs start from 1 again
        db.session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE categories_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE products_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE orders_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE order_items_id_seq RESTART WITH 1"))
        db.session.commit()

        return jsonify({"message": "All table data cleared successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
