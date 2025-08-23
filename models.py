from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Farmer")  # Farmer, Distributor, Retailer, Admin

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(64), unique=True, nullable=False)
    product_type = db.Column(db.String(64), nullable=False)
    origin = db.Column(db.String(128), nullable=False)
    
    # Link product to the user who owns it
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref='products')

    current_owner = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(64), default="Registered")
    product_metadata = db.Column(db.Text)  # store JSON string for temp/humidity/notes
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)