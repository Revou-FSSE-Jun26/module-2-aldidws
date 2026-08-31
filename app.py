import os
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask import Flask
from app import create_app
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    if debug:
        # Development: use Flask's built-in server
        app.run(debug=True)
    else:
        # Production: use Waitress (multi-threaded, works on Windows)
        from waitress import serve
        port = int(os.getenv('PORT', 5000))
        app.logger.info(f'Starting Waitress server on port {port} with 8 threads...')
        serve(app, host='0.0.0.0', port=port, threads=8)
