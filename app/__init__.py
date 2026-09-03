import os
import logging
import time
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

# OpenAPI/Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "RevoShop API",
        "description": "REST API for RevoShop: users, products, categories, and orders.",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header. Example: 'Bearer {token}'",
        }
    },
    "tags": [
        {"name": "Health", "description": "Service health checks"},
        {"name": "Auth", "description": "Registration and login"},
        {"name": "Users", "description": "User endpoints"},
        {"name": "Products", "description": "Product catalog endpoints"},
        {"name": "Categories", "description": "Category endpoints"},
        {"name": "Orders", "description": "Order endpoints (require authentication)"},
        {"name": "Seed", "description": "Database seeding utilities"},
    ],
}


def configure_logging(app):
    """Configure logging with console and file handlers."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_dir = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Log format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler - rotates at 10MB, keeps 10 backups
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Remove default Flask handlers to avoid duplicate logs
    app.logger.handlers.clear()

    # Apply to Flask app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # Suppress default Flask/Werkzeug duplicate logs in production
    if log_level != 'DEBUG':
        logging.getLogger('werkzeug').setLevel(logging.WARNING)


def register_request_hooks(app):
    """Register before/after request hooks for logging.
    Only logs individual requests in DEBUG mode to reduce I/O overhead under load.
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    @app.before_request
    def log_request_start():
        g.start_time = time.time()
        if log_level == 'DEBUG':
            app.logger.debug(
                'Request started: %s %s from %s',
                request.method,
                request.path,
                request.remote_addr
            )

    @app.after_request
    def log_request_end(response):
        duration = time.time() - g.get('start_time', time.time())
        # Only log slow requests (>1s) in production, all requests in DEBUG
        if log_level == 'DEBUG':
            app.logger.debug(
                'Request completed: %s %s - Status: %s - Duration: %.3fs',
                request.method,
                request.path,
                response.status_code,
                duration
            )
        elif duration > 1.0:
            app.logger.warning(
                'Slow request: %s %s - Status: %s - Duration: %.3fs',
                request.method,
                request.path,
                response.status_code,
                duration
            )
        return response


def register_error_handlers(app):
    """Register global error handlers with logging."""

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning('404 Not Found: %s %s', request.method, request.path)
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error('500 Internal Server Error: %s %s', request.method, request.path, exc_info=True)
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        app.logger.error(
            'Unhandled exception on %s %s: %s',
            request.method,
            request.path,
            str(error),
            exc_info=True
        )
        db.session.rollback()
        return {'error': 'Internal server error'}, 500


def create_app():
    app = Flask(__name__)

    # Sensitive config must be provided via environment. Fail fast rather than
    # silently falling back to an insecure default in production.
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise RuntimeError(
            'SECRET_KEY environment variable is required. '
            'Set it in your .env file (see .env.example).'
        )
    app.config['SECRET_KEY'] = secret_key

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise RuntimeError(
            'DATABASE_URL environment variable is required. '
            'Set it in your .env file (see .env.example).'
        )
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'

    # Connection pooling for better concurrency performance
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 20,
        'max_overflow': 30,
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Configure logging
    configure_logging(app)
    app.logger.info('Application starting up...')

    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize Swagger UI (available at /docs/)
    Swagger(app, config=swagger_config, template=swagger_template)

    # Import models so they are registered with SQLAlchemy
    from app.models import User, Product, Category, Order, order_items  # noqa: F401

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.seed import seed_bp
    from app.routes.users import user_bp
    from app.routes.products import product_bp
    from app.routes.categories import category_bp
    from app.routes.orders import order_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(seed_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(order_bp)

    # Register request logging hooks
    register_request_hooks(app)

    # Register error handlers
    register_error_handlers(app)

    app.logger.info('Application ready.')

    return app


# WSGI entrypoint: expose a module-level ``app`` so that ``gunicorn app:app``
# resolves. Importing the ``app`` package (this file) makes ``app.app`` the
# Flask instance built by the factory.
app = create_app()
