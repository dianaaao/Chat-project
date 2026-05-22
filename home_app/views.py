import flask, werkzeug.security as security, flask_login
from .apps import *
from .models import User
from app.db import DATABASE
from config import send_verification_email



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
                # first_name="Test",
                # last_name="User",   
                email = email,
                password_hash = pass_hash,
                is_verified = False,
            )
            DATABASE.session.add(user)
            DATABASE.session.commit()

            verifyurl = f"{flask.request.host_url}check_email?user_id={user.id}" # зібрали посилання
            send_verification_email(to_email = email, verify_url = verifyurl) # відправили листа з посиланням для підтвердження
            return flask.redirect("/success_page")
        
    return flask.render_template("registration.html", registration = True)


@registration.route("/check_email")
def check_email():
    user_id = flask.request.args.get("user_id")
    if user_id:
        user = User.query.filter_by(id = user_id).scalar()
        if user:
            user.is_verified = True
            DATABASE.session.commit()
            return flask.redirect("/main_page")
    
    return flask.render_template("registration.html", registration = True)


@main_page.route("/main_page", methods = ["GET", "POST"])
@flask_login.login_required # для безпеки, щоб не можна було зайти на головну сторінку без авторизації
def render_home():
    return flask.render_template("main_page.html", main_page = True)

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

@success_page.route("/success_page")
def render_success_page():
    return flask.render_template("success_page.html", success_page = True)

@main_page.route("/logout")
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login.render_login'))

