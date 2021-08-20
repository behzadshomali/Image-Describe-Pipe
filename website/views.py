from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from postgres import connect, add_defining_image
from .models import users

views = Blueprint('views', __name__)
conn = connect('123')


@views.route('/')
@views.route('/home')
# @login_required
def home():
    return render_template('home.html', user=current_user)


@views.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@views.route('/home/addImage', methods=['GET', 'POST'])
@views.route('/addImage', methods=['GET', 'POST'])
@login_required
def add_image():
    if request.method == 'POST':
        url = request.form.get('url')
        person = request.form.get('person')

        add_defining_image(conn, user_email=current_user.email,
                           image_url=url, who_is_in=person)
        flash('Image has been added to database successfully.', category='success')

    return render_template('add_image.html', user=current_user)
