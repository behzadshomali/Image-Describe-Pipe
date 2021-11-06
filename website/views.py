from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from postgres import connect, add_defining_image, evaluate_image
import os


views = Blueprint("views", __name__)
conn = connect("123")


@views.route("/")
@views.route("/home")
# @login_required
def home():
    return render_template("home.html", user=current_user)


@views.route("/home/addImage", methods=["GET", "POST"])
@views.route("/addImage", methods=["GET", "POST"])
@login_required
def add_image():
    if request.method == "POST":
        url = request.form.get("url")
        person = request.form.get("person")

        add_defining_image(
            conn, user_email=current_user.email, image_url=url, who_is_in=person
        )
        flash("Image has been added to database successfully.", category="success")

    return render_template("add_image.html", user=current_user)


@views.route("/home/describeImage", methods=["GET", "POST"])
@views.route("/describeImage", methods=["GET", "POST"])
@login_required
def describe_image():
    if request.method == "POST":
        url = request.form.get("url")

        scene_description = ""
        evaluate_image(conn, user_email=current_user.email, image_url=url)
        with open("output/scene_output.txt") as f:
            for line in f:
                scene_description += line

        emotions = ""
        with open("output/emotions_output.txt") as f:
            for line in f:
                emotions += line
                emotions += ", "
            emotions = emotions[:-2]
            emotions += "!"

        os.system("rm -r output/")

        return render_template(
            "describe_image.html",
            user=current_user,
            url=url,
            display="none",
            table_dis="none",
            res_table_dis="inline-table",
            scene_description=scene_description,
            emotions=emotions,
        )
    return render_template(
        "describe_image.html",
        user=current_user,
        display="block",
        table_dis="inline-table",
        res_table_dis="none",
        scene_description="",
        emotions="",
    )
