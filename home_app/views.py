import flask, werkzeug.security as security
from .apps import *
from .models import User
from app.db import DATABASE

# @main_page.route("/", methods = ["GET", "POST"])
# def render_home():
#     return flask.render_template("home.html")

@registration.route("/", methods = ["GET", "POST"])
def render_registration():
    
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")
    
        if email and password:
            if len(password) < 8:
                return flask.render_template(
                    "registration.html", 
                    error = "Password must be at least 8 characters long.",
                    registration = True,
                )

            check_user = User.query.filter_by(email = email).scalar()
            if check_user:
                return flask.render_template(
                    "registration.html", 
                    error = "User with this email already exists.",
                    registration = True,
                )
            
            pass_hash = security.generate_password_hash(password)
            user = User(
                first_name="Test",
                last_name="User",   
                email = email,
                password_hash = pass_hash,
            )
            DATABASE.session.add(user)
            DATABASE.session.commit()
    return flask.render_template("registration.html", registration = True)

@login.route("/login", methods = ["GET", "POST"])
def render_login():
    return flask.render_template("login.html")