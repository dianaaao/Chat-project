import flask, werkzeug.security as security, flask_login, datetime
from .apps import *
from .models import User, Group, UserGroup, Message
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

@main_page.route("/save_settings", methods = ["POST"])
@flask_login.login_required
def save_settings():
    first_name = flask.request.form.get("first_name", "").strip()
    last_name = flask.request.form.get("last_name", "").strip()
    username = flask.request.form.get("username", "").strip()
    gender  = flask.request.form.get("gender", "").strip()
    birth_date = flask.request.form.get("birth_date", "").strip()

    if first_name and last_name and username and gender and birth_date:
        unique_username = User.query.filter_by(username = username).scalar()
        if unique_username and unique_username.id != flask_login.current_user.id:
            return flask.redirect("/main_page")
        
        
        
        try:
            birth = datetime.date.fromisoformat(birth_date)
            if birth >= datetime.date.today():
                return flask.redirect("/main_page")
        except ValueError as error:
            print(error)    

        user = flask_login.current_user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.gender = gender
        user.birth_date = birth_date
        DATABASE.session.commit()
    else:
        return flask.redirect("/main_page")
    
    return flask.redirect("/main_page")
        


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

@main_page.route("/create_chat", methods = ["POST"])
@flask_login.login_required  # якщо юзер не залогінений — редірект на логін
def create_chat():
    owner_group = Group.query.filter_by(owner_id = flask_login.current_user.id).scalar()
    if owner_group:
        return flask.jsonify({"error": "already_exists"}), 400
    
    chat_name = flask.request.json.get("name", "").strip()
    if not chat_name:
        return flask.jsonify({"error": "empty_name"}), 400
    
    new_group = Group(group_name = chat_name, owner_id = flask_login.current_user.id)
    DATABASE.session.add(new_group)
    DATABASE.session.commit()
    
    user_group = UserGroup(
        user_id = flask_login.current_user.id,
        group_id = new_group.id
    )
    DATABASE.session.add(user_group)
    DATABASE.session.commit()
    

    return flask.jsonify({"id": new_group.id, "name": new_group.group_name}), 201

@main_page.route("/delete_chat", methods=["DELETE"])
@flask_login.login_required
def delete_chat():
    owner_group = Group.query.filter_by(owner_id = flask_login.current_user.id).scalar()
    if not owner_group:
        return flask.jsonify({"error": "already_exists"}), 400
    
    UserGroup.query.filter_by(group_id = owner_group.id).delete()
    DATABASE.session.delete(owner_group)
    DATABASE.session.commit()

    return flask.jsonify({"ok": True}), 200

@main_page.route("/my_chat", methods=["GET"])
@flask_login.login_required
def my_chat():
    owner_group = Group.query.filter_by(owner_id = flask_login.current_user.id).scalar()
    if owner_group:
        return flask.jsonify({"id": owner_group.id, "name": owner_group.group_name})
    
    return flask.jsonify({}), 200

@main_page.route("/search_chats", methods=["GET"])
@flask_login.login_required
def search_chats():
    query = flask.request.args.get("query", "").strip()
    if not query:
        return flask.jsonify([])

    groups = Group.query.filter(Group.group_name.ilike(f"%{query}%")).all()
    result = [{"id": group.id, "name": group.group_name} for group in groups]
    return flask.jsonify(result)

@main_page.route("/join_chat/<int:chat_id>", methods=["POST"])
@flask_login.login_required
def joing_chat(chat_id):
    group = Group.query.get(chat_id)
    if not group:
        return flask.jsonify({"error": "not_found"}), 404
    

    already_in_group = UserGroup.query.filter_by(user_id = flask_login.current_user.id, group_id=chat_id).first()
    if already_in_group:
        return flask.jsonify({"ok": True, "already_member": True})
    
    member = UserGroup(user_id = flask_login.current_user.id, group_id=chat_id)
    DATABASE.session.add(member)
    DATABASE.session.commit()

    return flask.jsonify({"ok": True}), 200

@main_page.route("/logout")
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login.render_login'))

@main_page.route('/chats/<int:chat_id>/')
@flask_login.login_required
def chat_page(chat_id):
    chat = Group.query.get_or_404(chat_id)
    messages = Message.query.filter_by(group_id = chat_id).order_by(Message.time_stamp).all()
    return flask.render_template('particles/chat_room.html', chat = chat, messages = messages)
    
@main_page.route('/get_chats', methods = ["GET"])
@flask_login.login_required
def get_chats():
    chats = Group.query.all()
    result = []
    for elements in chats:
        last_message = Message.query.filter_by(group_id = elements.id).order_by(Message.time_stamp.desc()).first()
        result.append({
            "id": elements.id,
            "name": elements.group_name,
            "last_message": last_message.text if last_message else "",
            "last_time": last_message.time_stamp.isoformat() if last_message else "" 
        })
    return flask.jsonify(result)

@main_page.route("/get_messages/<int:group_id>", methods=["GET"])
@flask_login.login_required
def get_messages(group_id):
    messages = Message.query.filter_by(group_id = group_id).order_by(Message.time_stamp).all()
    return flask.jsonify([{
        "text": msg.text,
        "author": msg.author.username or msg.author.email,
        "user_id": msg.user_id,
        "time": msg.time_stamp.strftime('%I:%M %p')
    } for msg in messages])


@main_page.route('/chats/<int:chat_id>/leave', methods=['POST'])
@flask_login.login_required
def leave_chat(chat_id):
    member = UserGroup.query.filter_by(group_id = chat_id, user_id = flask_login.current_user.id)
    if member:
        DATABASE.session.delete(member)
        DATABASE.session.commit()
    return flask.redirect(flask.url_for('main_page.main'))
    
