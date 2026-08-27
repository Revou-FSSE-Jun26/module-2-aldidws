from app import db

order_items = db.Table(
    "order_items",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("order_id", db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True),
    db.Column("product_id", db.Integer, db.ForeignKey("products.id"), nullable=False, index=True),
    db.Column("quantity", db.Integer, nullable=False),
    db.Column("price", db.Float, nullable=False),
)
