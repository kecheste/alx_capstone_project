from . import db
from flask_login import UserMixin
from datetime import datetime
from flask import current_app

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)    
    image = db.Column(db.String(255))
    author = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    num_read=db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())
    comments=db.relationship('Comments', backref='blogs',
    passive_deletes=True)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())
    author = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blogs.id', ondelete='CASCADE'), nullable=False)

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())
    posts=db.relationship('Blogs', backref='user',
    passive_deletes=True)
    comments=db.relationship('Comments', backref='user',
    passive_deletes=True)
    prof_views=db.Column(db.Integer, default=0)
    prof_image=db.Column(db.String(100), nullable=True)

    def __init__(self, email, password, username):
        self.email = email
        self.username = username
        self.password = password
    def is_active(self):
       return True
