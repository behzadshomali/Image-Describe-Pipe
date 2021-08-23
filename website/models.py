from flask_login import UserMixin
from . import db
from sqlalchemy.sql import func

class users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    full_name = db.Column(db.String(1000))
    register_time = db.Column(db.DateTime(timezone=True), default=func.now())
    lastlogin = db.Column(db.DateTime(timezone=True), default=func.now())
    age = db.Column()