from flask import Blueprint, jsonify
from sqlalchemy import text
from app import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"message": "Flask is connected to PostgreSQL!", "status": "ok"})
    except Exception as e:
        return jsonify({"message": "Failed to connect to PostgreSQL", "status": "error", "error": str(e)})
