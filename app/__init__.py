from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:aldi17@localhost:5432/revoshop_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so they are registered with SQLAlchemy
    from app.models import User, Product, Category, Order, OrderItem  # noqa: F401

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.seed import seed_bp
    from app.routes.users import user_bp
    from app.routes.products import product_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(seed_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)

    with app.app_context():
        db.create_all()

    return app
