from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    partner1_name = db.Column(db.String(100), nullable=False)
    partner2_name = db.Column(db.String(100), nullable=False)
    wedding_date = db.Column(db.Date, nullable=False)
    wedding_location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    registry = db.relationship('Registry', backref='user', uselist=False)
    guests = db.relationship('Guest', backref='user', lazy=True)
    wedding_party = db.relationship('WeddingPartyMember', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Registry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('RegistryItem', backref='registry', lazy=True)

class RegistryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registry_id = db.Column(db.Integer, db.ForeignKey('registry.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    item_type = db.Column(db.String(20), default='physical')  # physical, cash, experience
    price = db.Column(db.Float)
    target_amount = db.Column(db.Float)  # For cash funds
    current_amount = db.Column(db.Float, default=0)  # For tracking cash contributions
    amazon_url = db.Column(db.String(1000))
    is_purchased = db.Column(db.Boolean, default=False)
    purchased_by = db.Column(db.String(100))
    ship_to_couple = db.Column(db.Boolean, default=True)
    bring_to_wedding = db.Column(db.Boolean, default=False)
    shipping_address = db.Column(db.Text)
    purchase_date = db.Column(db.DateTime)
    experience_date = db.Column(db.Date)  # For experience gifts
    experience_location = db.Column(db.String(200))  # For experience gifts
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    rsvp_status = db.Column(db.String(20), default='pending')  # pending, attending, not_attending
    number_of_guests = db.Column(db.Integer, default=1)
    dietary_restrictions = db.Column(db.Text)
    notes = db.Column(db.Text)
    table_assignment = db.Column(db.String(50))  # For table assignments (e.g., "Table 1")
    meal_choice = db.Column(db.String(20))  # For meal selection
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WeddingPartyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role_type = db.Column(db.String(20), nullable=False)  # 'bridesmaid', 'groomsman', 'sponsor'
    role_title = db.Column(db.String(50))  # e.g., 'Maid of Honor', 'Best Man', 'Primary Sponsor'
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)