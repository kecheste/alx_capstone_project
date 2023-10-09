from app import db
from flask_login import UserMixin
from datetime import datetime

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)    
    image = db.Column(db.String(255))    
    author = db.Column(db.Integer)    
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())    


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())
    def __init__(self, email, password, username):
        self.email = email
        self.username = username
        self.password = password
    def is_active(self):
       return True