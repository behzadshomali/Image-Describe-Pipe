from flask import Flask
from flask_login import LoginManager
from os import path

def create_app():
    print('dddddd')
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'idp'
    
    from .views import viewss
    from .auth import auth
    from .models import User

    app.register_blueprint(viewss, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app