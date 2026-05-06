import flask, werkzeug.security as security, flask_login
from .apps import *
from .models import User
from app.db import DATABASE



@registration.route("/", methods = ["GET", "POST"])
def render_registration():
    if flask_login.current_user.is_authenticated:
        return flask.render_template("main_page.html", main_page = True)
    
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")
    
        if email and password:
            if len(password) < 8:
                return flask.render_template(
                    "registration.html", 
                    registration = True,
                )

            check_user = User.query.filter_by(email = email).scalar()
            if check_user:
                return flask.render_template(
                    "registration.html", 
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
            return flask.redirect("/main_page")
        
    return flask.render_template("registration.html", registration = True)

@main_page.route("/main_page", methods = ["GET", "POST"])
@flask_login.login_required
def render_home():
    return flask.render_template("main_page.html", main_page=True)

@login.route("/login", methods = ["GET", "POST"])
def render_login():
    if flask_login.current_user.is_authenticated:
        return flask.redirect("/main_page")
    
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")

        if email and password:
            user = User.query.filter_by(email = email).scalar()
            if user and security.check_password_hash(user.password_hash, password):
                flask_login.login_user(user)
                return flask.redirect("/main_page")

    return flask.render_template("login.html", login = True)

@main_page.route("/logout")
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login.render_login'))
    
    # render_template(
    #     template_name_or_list = "login.html", 
    #     login = True,
    # )