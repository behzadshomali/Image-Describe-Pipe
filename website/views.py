from flask import Blueprint, render_template

viewss = Blueprint('views', __name__)

@viewss.route('/')
@viewss.route('/home')
def home():
    return render_template('home.html')