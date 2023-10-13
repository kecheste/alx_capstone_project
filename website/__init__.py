from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv
load_dotenv()

db = SQLAlchemy()

def create_app():

    cloud_name = os.environ.get('CLOUD_NAME')
    api_key = os.environ.get('API_KEY')
    api_secret = os.environ.get('API_SECRET')
    secret_key = os.environ.get('SECRET_KEY')
    database_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    mail_server = os.environ.get('MAIL_SERVER')
    mail_port = os.environ.get('MAIL_PORT')
    mail_username = os.environ.get('MAIL_USERNAME')
    mail_password = os.environ.get('MAIL_PASSWORD')
    mail_ssl = os.environ.get('MAIL_USE_SSL')

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SECRET_KEY'] = secret_key
    app.config['CLOUD_NAME'] = cloud_name
    app.config['API_KEY'] = api_key
    app.config['API_SECRET'] = api_secret
    app.config['MAIL_SERVER'] = mail_server
    app.config['MAIL_PORT'] = mail_port
    app.config['MAIL_USERNAME'] = mail_username
    app.config['MAIL_PASSWORD'] = mail_password
    app.config['MAIL_USE_SSL'] = mail_ssl

    app.app_context().push()
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Users

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter(Users.id == user_id).first()

    return app
