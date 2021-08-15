from flask import Flask
from os import path



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'idp'
    
    from .main import main
    from .auth import auth

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app