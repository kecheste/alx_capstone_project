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

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/flask-blog'
    app.config['SECRET_KEY'] = '2jZPfZd37nxIHstN'
    app.config['CLOUD_NAME'] = cloud_name
    app.config['API_KEY'] = api_key
    app.config['API_SECRET'] = api_secret

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
