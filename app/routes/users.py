from flask import Blueprint, jsonify, request
from app.controllers import user_controller

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['GET'])
def get_all_users():
    """List all users
    ---
    tags:
      - Users
    responses:
      200:
        description: A list of users
    """
    result, status = user_controller.get_all_users()
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get a single user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user
    responses:
      200:
        description: The requested user
      404:
        description: User not found
    """
    result, status = user_controller.get_single_user(user_id)
    return jsonify(result), status


@user_bp.route('/register', methods=['POST'])
def register_user():
    """Register a new user
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: john_doe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: secret123
    responses:
      201:
        description: User created
      400:
        description: Invalid input or user already exists
    """
    data = request.get_json(silent=True) or {}
    result, status = user_controller.register_user(data)
    return jsonify(result), status


@user_bp.route('/auth/login', methods=['POST'])
def login():
    """Login and obtain a JWT token
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: secret123
    responses:
      200:
        description: Login successful, returns a JWT token
      401:
        description: Invalid credentials
    """
    data = request.get_json(silent=True) or {}
    result, status = user_controller.login(data)
    return jsonify(result), status
