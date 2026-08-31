from dotenv import load_dotenv

load_dotenv()

# Reuse the module-level app created in app/__init__.py so both
# ``gunicorn wsgi:app`` and ``gunicorn app:app`` resolve to the same instance.
from app import app

if __name__ == '__main__':
    app.run()
