from flask import Blueprint, render_template, redirect, url_for, request, flash
from postgres import connect, login_user_db
import datetime
from .models import users
from datetime import timedelta
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re

conn = connect('123')

def is_password_ok(password, repeated_password):
    if password != repeated_password:
        flash('Password doesn\'t match!', category='danger')
        print('bad password')
        return False
    if len(password)<8:
        flash('short password', category='danger')
        print('short password')
        return False
    if not re.search("[a-z]",password):
        flash('Password doesn\'t match!', category='danger')
        print('bad password')
        return False
    if not re.search("[A-Z]", password):
        flash('Password must contain at least one Uppercase letter', category='danger')
        print('Password must contain at least one Uppercase letter') 
        return False    
    if not re.search("[0-9]", password):
        flash('Password must contain at least one digit') 
        print('Password must contain at least one digit') 
        return False
    if not re.search("[_@$!]", password):   
        flash('Password must contain at least one special character', category='danger')
        print('Password must contain at least one special character') 
        return False  
    if re.search("\s", password):
        flash('the field is empty', category='danger')
        print('the field is empty')
        return False  
    
    return True


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        email=email.lower()
        password = request.form.get('password')
        user = users.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True, duration=timedelta(minutes=30))
                login_user_db(conn, current_user.email)
                flash('Logged in!', category='success')
                return redirect(url_for('views.home'))
            else:
               flash('Password is incorrect.', category='danger') 
        else:
            flash('The user does not exist.', category='danger')

    return render_template('login.html' , user=current_user)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out!', category='success')
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        birth_date = request.form.get('birthDate')
        password = request.form.get('password1')
        repeated_password = request.form.get('password2')

        user = users.query.filter_by(email=email).first()

        if user:
            flash('The user already exists!', category='danger')
            print('exists')
        elif is_password_ok(password, repeated_password):   
            age = datetime.datetime.now().year - int(birth_date)
            full_name = first_name + ' ' + last_name
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = users(email=email, age=age, password=hashed_password, full_name=full_name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True, duration=timedelta(minutes=30))
            login_user_db(conn, current_user.email)

            flash('User created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)
    