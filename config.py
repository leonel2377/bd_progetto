import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Configurazione di base
    SECRET_KEY = 'chiave-sviluppo-flask-app-2024'
    
    # Configurazione Database - PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:7999@localhost:5432/flight_booking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurazione JWT
    JWT_SECRET_KEY = 'jwt-chiave-sviluppo-2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configurazione Mail (per future implementazioni)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configurazione Upload File
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configurazione Sessioni
    PERMANENT_SESSION_LIFETIME = 3600  # 1 ora
    
    # Configurazione Sicurezza (disabilitata in sviluppo)
    SESSION_COOKIE_SECURE = False  # Cambiato da True a False per sviluppo
    REMEMBER_COOKIE_SECURE = False  # Cambiato da True a False per sviluppo
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True 