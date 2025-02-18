import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev_key_123")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Create tables
with app.app_context():
    # Import all models to ensure they're registered with SQLAlchemy
    from models import (
        User, Registry, RegistryItem, Guest, 
        WeddingPartyMember, Wedding, Quinceanera,
        GiftSuggestion
    )

    # Create all tables
    db.create_all()

    # Log table creation using SQLAlchemy inspector
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    logging.info(f"Created tables: {tables}")

# Register blueprints
from routes import main, auth, registry, guest, services
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(registry)
app.register_blueprint(guest)
app.register_blueprint(services)