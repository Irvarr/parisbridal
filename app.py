import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

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
    import models
    db.create_all()

# Register blueprints
from routes import main, auth, registry, guest, services
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(registry)
app.register_blueprint(guest)
app.register_blueprint(services)