from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__)
    
    # Configuration - imports différés
    from app.utils.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
    
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = 'weather-service-secret-key-2024'

    # Configuration du pool de connexions
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
    }

    # Initialisation des extensions
    db.init_app(app)

    # Enregistrement des blueprints APRÈS initialisation
    with app.app_context():
        from app.routes import weather_bp  # Import différé
        app.register_blueprint(weather_bp)  # Ajout url_prefix

    # Création des tables
    with app.app_context():
        db.create_all()

    return app