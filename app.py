import os
import logging
from flask import Flask, render_template
from models import db
from routes.auth import auth_bp
from routes.marketplace import marketplace_bp
from routes.crm import crm_bp
from routes.api import api_bp

def create_app():
    app = Flask(__name__)

    # ââ Configuration âââââââââââââââââââââââââââââââââââââââââââââââââ
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database: use DATABASE_URL (PostgreSQL on Railway) or fall back to SQLite
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///marketplace.db')
    # Railway/Heroku provide postgres:// but SQLAlchemy needs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images', 'uploads')

    # CSRF and security settings
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # ââ Logging âââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    if os.environ.get('FLASK_ENV') == 'production':
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
        app.logger.info('MarketHub starting in production mode')
    else:
        logging.basicConfig(level=logging.DEBUG)

    # ââ Database ââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    db.init_app(app)

    # ââ Blueprints ââââââââââââââââââââââââââââââââââââââââââââââââââââ
    app.register_blueprint(auth_bp)
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(crm_bp, url_prefix='/crm')
    app.register_blueprint(api_bp, url_prefix='/api')

    # ââ Error handlers ââââââââââââââââââââââââââââââââââââââââââââââââ
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f'Server error: {e}')
        return render_template('errors/500.html'), 500

    # ââ Create tables âââââââââââââââââââââââââââââââââââââââââââââââââ
    with app.app_context():
        db.create_all()

    return app

# Entry point for local dev
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
