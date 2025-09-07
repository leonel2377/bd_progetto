from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig

# Inizializzazione delle estensioni
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inizializzazione delle estensioni con l'app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configurazione del login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Per favore effettua il login per accedere a questa pagina.'
    login_manager.login_message_category = 'info'

    # Registrazione dei blueprint
    from app.routes import main, auth, airline, passenger, api
    app.register_blueprint(main.main)
    app.register_blueprint(auth.auth)
    app.register_blueprint(airline.airline)
    app.register_blueprint(passenger.passenger)
    app.register_blueprint(api.api)

    # Creazione delle cartelle necessarie
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    return app

from app import models 