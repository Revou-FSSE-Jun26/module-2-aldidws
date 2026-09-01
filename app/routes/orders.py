from flask import Blueprint, jsonify, request
from app.middleware.auth import token_required, owner_required
from app.controllers import order_controller

order_bp = Blueprint('order', __name__)


@order_bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    """Place a new order
    Requires a valid JWT. The order is linked to the authenticated user.
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - items
          properties:
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                    example: 1
                  quantity:
                    type: integer
                    example: 2
    responses:
      201:
        description: Order created
      400:
        description: Invalid input
      401:
        description: Missing or invalid token
    """
    data = request.get_json()
    result, status = order_controller.create_order(current_user, data)
    return jsonify(result), status


@order_bp.route('/orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    """List all orders for the current user
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    responses:
      200:
        description: A list of the authenticated user's orders
      401:
        description: Missing or invalid token
    """
    result, status = order_controller.get_user_orders(current_user)
    return jsonify(result), status


@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    """View a specific order
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: ID of the order
    responses:
      200:
        description: The requested order
      401:
        description: Missing or invalid token
      404:
        description: Order not found
    """
    result, status = order_controller.get_order(current_user, order_id)
    return jsonify(result), status


@order_bp.route('/orders/<int:order_id>', methods=['PUT'])
@token_required
@owner_required
def update_order_route(current_user, order_id):
    """Update an order
    Only the owner of the order may update it. Currently supports updating status.
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: ID of the order
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [pending, paid, shipped, completed, cancelled]
              example: shipped
    responses:
      200:
        description: Order updated
      400:
        description: Invalid input
      401:
        description: Missing or invalid token
      403:
        description: Not the owner of this order
      404:
        description: Order not found
    """
    data = request.get_json(silent=True) or {}
    result, status = order_controller.update_order(current_user, order_id, data)
    return jsonify(result), status


@order_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@token_required
@owner_required
def delete_order(current_user, order_id):
    """Delete an order
    Only the owner of the order may delete it.
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: ID of the order
    responses:
      200:
        description: Order deleted
      401:
        description: Missing or invalid token
      403:
        description: Not the owner of this order
      404:
        description: Order not found
    """
    result, status = order_controller.delete_order(current_user, order_id)
    return jsonify(result), status
