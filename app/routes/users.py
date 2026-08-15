from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from app import db
from app.models import User

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_data = [user.to_dict() for user in users]
    return jsonify(users_data), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"error": "User not found"}), 404


@user_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'username, email and password are required'}), 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'email already registered'}), 409

    return jsonify(user.to_dict()), 201
