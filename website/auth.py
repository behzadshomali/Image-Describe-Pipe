from flask import Blueprint, render_template, redirect, url_for, request, flash
from postgres import add_user, connect
import datetime
 

auth = Blueprint('auth', __name__)

conn = connect('beh9722762451')



@auth.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    return render_template('login.html')

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
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

        cur = conn.cursor()
        cur.execute(
            f'''
            SELECT email
            FROM public.users
            WHERE email = '{email}'
            '''
        )
        user_exists = len(cur.fetchall())
        
        if user_exists:
            flash('The user already exists!', category='danger')
            print('exists')
        elif password != repeated_password:
            flash('Password doesn\'t match!', category='danger')
            print('bad password')
        else:
            print('good')
            age = datetime.datetime.now().year - int(birth_date)
            full_name = first_name + ' ' + last_name
            add_user(
                conn,
                full_name,
                age,
                email,
                password
            )
            flash('User created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html')
    