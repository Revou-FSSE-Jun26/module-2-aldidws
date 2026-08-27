import datetime as dt
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import jwt
from app import db
from app.models import User


def get_all_users():
    """Retrieve all users."""
    users = User.query.all()
    return [user.to_dict() for user in users], 200


def get_single_user(user_id):
    """Retrieve a single user by ID."""
    user = db.session.get(User, user_id)
    if user:
        return user.to_dict(), 200
    return {"error": "User not found"}, 404


def register_user(data):
    """Register a new user."""
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not username or not email or not password:
        return {'error': 'username, email and password are required'}, 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'email already registered'}, 409

    return user.to_dict(), 201


def login(data):
    """Authenticate user and return JWT token."""
    email = data.get('email')
    password = data.get('password')

    current_app.logger.info('Login attempt for email: %s', email)
    if not email or not password:
        return {'error': 'email and password are required'}, 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return {'error': 'invalid email or password'}, 401

    token = jwt.encode(
        {
            'user_id': user.id,
            'role': user.role,
            'exp': dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=24)
        },
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return {'token': token, 'user': user.to_dict()}, 200
