from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app import db
from app.models import Order, Product
from app.models.order_item import order_items


def create_order(current_user, data):
    """Place a new order for the current user."""
    if not data or not data.get('items'):
        return {"error": "Missing required field: items"}, 400

    items = data['items']

    # Validate input format
    for item in items:
        if not item.get('product_id') or not item.get('quantity'):
            return {"error": "Each item must have product_id and quantity"}, 400

    # Fetch all needed products in ONE query instead of N queries
    product_ids = [item['product_id'] for item in items]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    product_map = {p.id: p for p in products}

    # Validate stock and calculate total
    total_amount = 0
    for item in items:
        product = product_map.get(item['product_id'])
        if not product:
            return {"error": f"Product with id {item['product_id']} not found"}, 404
        if product.stock < item['quantity']:
            return {"error": f"Insufficient stock for product '{product.name}'"}, 400
        total_amount += product.price * item['quantity']

    # Create the order
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status='pending'
    )
    db.session.add(new_order)
    db.session.flush()

    # Insert order items and reduce stock
    for item in items:
        product = product_map[item['product_id']]
        product.stock -= item['quantity']

        db.session.execute(order_items.insert().values(
            order_id=new_order.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=product.price
        ))

    try:
        db.session.commit()
        return {"message": "Order placed successfully", "order": new_order.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to place order: {str(e)}"}, 500


def get_user_orders(current_user):
    """List all orders for the current user."""
    orders = Order.query.filter_by(user_id=current_user.id, is_deleted=False).all()
    return [order.to_dict() for order in orders], 200


def get_order(current_user, order_id):
    """View a specific order with items and product details."""
    order = db.session.get(Order, order_id)

    if not order:
        return {"error": "Order not found"}, 404

    if order.user_id != current_user.id:
        return {"error": "Unauthorized access to this order"}, 403

    # Single JOIN query instead of N+1
    items_with_products = db.session.execute(
        db.select(
            order_items.c.id,
            order_items.c.product_id,
            order_items.c.quantity,
            order_items.c.price,
            Product.name.label('product_name')
        ).select_from(
            order_items.join(Product, order_items.c.product_id == Product.id)
        ).where(order_items.c.order_id == order.id)
    ).fetchall()

    order_data = order.to_dict()
    order_data['items'] = [
        {
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "price": item.price
        }
        for item in items_with_products
    ]

    return order_data, 200


VALID_STATUSES = {'pending', 'paid', 'shipped', 'completed', 'cancelled'}


def update_order(current_user, order_id, data):
    """Update an existing order's status. Only the owner may update it."""
    order = db.session.get(Order, order_id)

    if not order or order.is_deleted:
        return {"error": "Order not found"}, 404

    if order.user_id != current_user.id:
        return {"error": "Unauthorized access to this order"}, 403

    if not data or 'status' not in data:
        return {"error": "Missing required field: status"}, 400

    new_status = data['status']
    if new_status not in VALID_STATUSES:
        return {
            "error": f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        }, 400

    try:
        order.status = new_status
        db.session.commit()
        return {"message": "Order updated successfully", "order": order.to_dict()}, 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"Failed to update order: {str(e)}"}, 500


def delete_order(current_user, order_id):
    """Soft delete an order."""
    order = db.session.get(Order, order_id)

    if not order:
        return {"error": "Order not found"}, 404

    if order.is_deleted:
        return {"error": "Order already deleted"}, 404

    try:
        order.is_deleted = True
        db.session.commit()
        return {"message": "Order successfully deleted"}, 200
    except IntegrityError as e:
        db.session.rollback()
        return {"error": f"Cannot delete order due to integrity constraint: {str(e)}"}, 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"Failed to delete order: {str(e)}"}, 500
