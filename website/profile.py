from flask import Blueprint, render_template, request, flash, redirect
from flask.helpers import url_for
from flask_login import login_required, current_user, logout_user
from postgres import connect, remove_user as db_remove_user, remove_defining_image, get_images


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
    if request.method == 'POST':
        urls = request.form.getlist('urls')
        
        if urls:
            for url in urls:
                remove_defining_image(conn, current_user.email, url)

    return render_template('remove_image.html', user=current_user, images_urls=result)



    
    
