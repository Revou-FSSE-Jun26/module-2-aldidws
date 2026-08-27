from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app import db
from app.models import User


def token_required(f):
    """Middleware to verify JWT token and inject current_user."""
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
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                return jsonify({"error": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def owner_required(f):
    """Middleware to verify the current user owns the order."""
    @wraps(f)
    def decorated(current_user, order_id, *args, **kwargs):
        from app.models import Order
        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        if order.user_id != current_user.id:
            return jsonify({"error": "Unauthorized access to this order"}), 403
        return f(current_user, order_id, *args, **kwargs)
    return decorated
