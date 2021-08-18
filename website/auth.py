from flask import Blueprint, render_template, redirect, url_for, request, flash
from postgres import add_user, connect
import datetime
from .models import users
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
auth = Blueprint('auth', __name__)

# conn = connect('beh9722762451')



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
               flash('Password is incorrect.', category='danger') 
        else:
            flash('The user does not exist.', category='danger')

    return render_template('login.html')

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out!', category='success')
    return redirect(url_for('main.home'))

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
        elif password != repeated_password:
            flash('Password doesn\'t match!', category='danger')
            print('bad password')
        elif len(password)<8:
            flash('Password doesn\'t match!', category='danger')
            print('short password')
        elif not re.search("[a-z]",password):
            flash('Password doesn\'t match!', category='danger')
            print('bad password')
        elif not re.search("[A-Z]", password):
            flash('Password doesn\'t match!', category='danger')
            print('Password must contain atleast one uppercase letter')     
        elif not re.search("[0-9]", password):
            flash('Password must contain at least one digit')  
        elif not re.search("[_@$]", password):   
            flash('Password doesn\'t match!', category='danger')
            print('Password must contain at least one character')   
        elif re.search("\s", password):
              flash('Password doesn\'t match!', category='danger')
              print('the field is empty')      
        else:
            print('good')
            age = datetime.datetime.now().year - int(birth_date)
            full_name = first_name + ' ' + last_name
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = users(email=email, age=age, password=hashed_password, full_name=full_name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html')
    