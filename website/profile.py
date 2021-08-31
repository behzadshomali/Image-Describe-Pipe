from flask import Blueprint, render_template, request, flash, redirect
from flask.helpers import url_for
from flask_login import login_required, current_user, logout_user
from postgres import connect, remove_user as db_remove_user, remove_defining_image, get_images, replace_password
from .auth import is_password_ok
from werkzeug.security import generate_password_hash, check_password_hash


prof = Blueprint('profile', __name__)
conn = connect('123')


@prof.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@prof.route('/profile/removeUser', methods=['GET', 'POST'])
@login_required
def remove_user():
    if request.method == 'POST':
        verification = request.form.get('verification')
        if verification == "Delete the profile":
            user_email = current_user.email
            db_remove_user(conn, user_email)
            logout_user()
            flash('The profile was successfully removed', category='success')
            return redirect(url_for('views.home'))
        else:
            flash("The input doesn't match!", category='danger')

    return render_template('remove_user.html', user=current_user)


@prof.route('/profile/removeImage', methods=['GET', 'POST'])
@login_required
def remove_image():
    result = get_images(conn, current_user.email)
    if not result:
        result = []

    if request.method == 'POST':
        urls = request.form.getlist('urls')

        if urls:
            for url in urls:
                remove_defining_image(conn, current_user.email, url)

    return render_template('remove_image.html', user=current_user, images_urls=result)


@prof.route('/profile/changePassword', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        hashed_current_password = current_user.password
        entered_current_password = request.form.get('currentPassword')

        if check_password_hash(hashed_current_password, entered_current_password):
            new_password = request.form.get('newPassword1')
            repeated_new_password = request.form.get('newPassword2')
            if check_password_hash(hashed_current_password, new_password):
                flash("New password can't be the same as old password",
                      category='danger')
            elif is_password_ok(new_password, repeated_new_password):
                hashed_new_password = generate_password_hash(
                    new_password, method='sha256')
                replace_password(conn, current_user.email, hashed_new_password)
                flash('Password changed successfully!', category='success')
                return redirect(url_for('profile.profile'))
        else:
            flash("Current password isn't correct", category='danger')

    return render_template('change_password.html', user=current_user)
