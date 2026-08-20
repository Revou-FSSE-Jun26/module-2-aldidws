from flask import Blueprint, jsonify, request, current_app
from functools import wraps
import jwt
from app.models import Order, Product, User
from app.models.order_item import order_items
from app import db

order_bp = Blueprint('order', __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({"error": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)
    return decorated


#--- Place a new order linked to the logged-in user
@order_bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json()

    if not data or not data.get('items'):
        return jsonify({"error": "Missing required field: items"}), 400

    items = data['items']
    total_amount = 0

    # Validate all items first
    for item in items:
        if not item.get('product_id') or not item.get('quantity'):
            return jsonify({"error": "Each item must have product_id and quantity"}), 400

        product = Product.query.get(item['product_id'])
        if not product:
            return jsonify({"error": f"Product with id {item['product_id']} not found"}), 404
        if product.stock < item['quantity']:
            return jsonify({"error": f"Insufficient stock for product '{product.name}'"}), 400

        total_amount += product.price * item['quantity']

    # Create the order
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status='pending'
    )
    db.session.add(new_order)
    db.session.flush()  # Get the order ID

    # Insert order items and reduce stock
    for item in items:
        product = Product.query.get(item['product_id'])
        product.stock -= item['quantity']

        db.session.execute(order_items.insert().values(
            order_id=new_order.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=product.price
        ))

    try:
        db.session.commit()
        return jsonify({
            "message": "Order placed successfully",
            "order": new_order.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to place order: {str(e)}"}), 500


#--- List all orders for the current user
@order_bp.route('/orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return jsonify([order.to_dict() for order in orders]), 200


#--- View a specific order with its order items and product details
@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.user_id != current_user.id:
        return jsonify({"error": "Unauthorized access to this order"}), 403

    # Get order items with product details
    items_query = db.session.execute(
        order_items.select().where(order_items.c.order_id == order.id)
    ).fetchall()

    order_data = order.to_dict()
    order_data['items'] = []

    for item in items_query:
        product = Product.query.get(item.product_id)
        order_data['items'].append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "quantity": item.quantity,
            "price": item.price
        })

    return jsonify(order_data), 200


#--- Delete an order
@order_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@token_required
def delete_order(current_user, order_id):
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.user_id != current_user.id:
        return jsonify({"error": "Unauthorized access to this order"}), 403

    try:
        # Delete order items first
        db.session.execute(
            order_items.delete().where(order_items.c.order_id == order.id)
        )
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order successfully deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete order: {str(e)}"}), 500
