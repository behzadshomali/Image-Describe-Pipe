from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()

USER = 'postgres'
PASSWORD = 123
DB_NAME = 'Image describe pipe DB'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'idp'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USER}:{PASSWORD}@localhost/{DB_NAME}'
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    from .models import users

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(email):
        return users.query.get(email)

    return app