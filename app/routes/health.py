from flask import Blueprint, jsonify
from sqlalchemy import text
from app import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/')
def index():
    """API root
    Returns basic service info and useful links.
    ---
    tags:
      - Health
    responses:
      200:
        description: Service info
        schema:
          type: object
          properties:
            service:
              type: string
            status:
              type: string
            docs:
              type: string
    """
    return jsonify({
        "service": "RevoShop API",
        "status": "ok",
        "docs": "/docs/",
        "health": "/health"
    })


@health_bp.route('/health')
def health_check():
    """Health check
    Verifies the service is up and can reach PostgreSQL.
    ---
    tags:
      - Health
    responses:
      200:
        description: Service status
        schema:
          type: object
          properties:
            message:
              type: string
            status:
              type: string
    """
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"message": "Flask is connected to PostgreSQL!", "status": "ok"})
    except Exception as e:
        return jsonify({"message": "Failed to connect to PostgreSQL", "status": "error", "error": str(e)})
