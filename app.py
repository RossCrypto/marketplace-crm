import os
from flask import Flask
from models import db
from routes.auth import auth_bp
from routes.marketplace import marketplace_bp
from routes.crm import crm_bp
from routes.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images', 'uploads')

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(crm_bp, url_prefix='/crm')
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
