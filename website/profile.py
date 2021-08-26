from flask import Blueprint, render_template, request, flash, redirect
from flask.helpers import url_for
from flask_login import login_required, current_user, logout_user
from postgres import connect, remove_user as db_remove_user, remove_defining_image


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
    


# @views.route('/home/describeImage', methods=['GET', 'POST'])
# @views.route('/describeImage', methods=['GET', 'POST'])
# @login_required
# def describe_image():
#     if request.method == 'POST':
#         url = request.form.get('url')

#         scene_description = ''
#         evaluate_image(conn, user_email=current_user.email, image_url=url)
#         with open("output/scene_output.txt") as f:
#             for line in f:
#                 scene_description += line

#         emotions = ''
#         with open("output/emotions_output.txt") as f:
#             for line in f:
#                 emotions += line
#                 emotions += ', '
#             emotions = emotions[:-2]
#             emotions += '!'

#         os.system('rm -r output/')
        
#         flash('Image has been added to database successfully.', category='success')

#         return render_template('describe_image.html',
#                                user=current_user,
#                                url=url, display='none',
#                                table_dis='none',
#                                res_table_dis='inline-table',
#                                scene_description=scene_description,
#                                emotions=emotions)
#     return render_template('describe_image.html',
#                            user=current_user,
#                            display='block',
#                            table_dis='inline-table',
#                            res_table_dis='none',
#                            scene_description='',
#                            emotions='')
