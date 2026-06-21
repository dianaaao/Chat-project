import flask, werkzeug.security as security, flask_login, datetime
from .apps import *
from .models import User, Group, UserGroup, Message
from app.db import DATABASE
from config import send_verification_email
from .sockets import online_users, socketio



@registration.route("/", methods = ["GET", "POST"])
def render_registration():
    if flask_login.current_user.is_authenticated:
        # group = Group.query.get()
        # member_data = {
        #     "title": group.group_name,
        #     "members": [],
        # }
        # users = group.users
        # for user in users:
        #     member_data["members"].append({"email": user.email})

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

# Маршрут доступний тільки через POST запит (fetch з JS)
@main_page.route("/create_chat", methods = ["POST"])
@flask_login.login_required  # якщо юзер не залогінений — редірект на логін
def create_chat():
    # Шукаємо в БД чи є вже група де owner_id = id поточного юзера
    # .first() — повертає першу знайдену або None
    existing = Group.query.filter_by(owner_id=flask_login.current_user.id).first()
    if existing:
        # Юзер вже має чат — повертаємо помилку з кодом 400 (Bad Request)
        return flask.jsonify({"error": "already_exists"}), 400

    # Беремо назву чату з JSON тіла запиту який прийшов з fetch
    # "" — дефолтне значення якщо "name" не прийшло
    # .strip() — прибираємо пробіли по краях
    chat_name = flask.request.json.get("name", "").strip()
    if not chat_name:
        # Назва порожня — повертаємо помилку
        return flask.jsonify({"error": "empty_name"}), 400
    
    # Створюємо новий об'єкт Group (але ще не зберігаємо в БД)
    new_group = Group(group_name = chat_name, owner_id = flask_login.current_user.id)
    DATABASE.session.add(new_group)   # додаємо в сесію
    DATABASE.session.commit()         # зберігаємо в БД, після цього new_group.id вже існує

    # Створюємо запис що поточний юзер є учасником свого ж чату
    user_group = UserGroup(user_id = flask_login.current_user.id, group_id = new_group.id)
    DATABASE.session.add(user_group)
    DATABASE.session.commit()         # зберігаємо в БД
    
    # Повертаємо дані нового чату — JS отримає { id: 1, name: "..." }
    # 201 — Created (стандартний код для успішного створення)
    return flask.jsonify({"id": new_group.id, "name": new_group.group_name}), 201


@main_page.route("/delete_chat", methods=["DELETE"])
@flask_login.login_required
def delete_chat():
    # Шукаємо чат поточного юзера по owner_id
    group = Group.query.filter_by(owner_id=flask_login.current_user.id).first()
    if not group:
        # Чат не знайдено — 404 Not Found
        return flask.jsonify({"error": "not_found"}), 404
    
    group_id = group.id  # зберігаємо id до видалення 
    # спочатку видаляємо повідомлення
    Message.query.filter_by(group_id=group.id).delete()
    # Спочатку видаляємо всіх учасників чату з таблиці UserGroup
    # ВАЖЛИВО: робимо це ДО видалення групи, бо інакше буде помилка foreign key
    UserGroup.query.filter_by(group_id=group.id).delete()
    DATABASE.session.delete(group)  # видаляємо саму групу
    DATABASE.session.commit()       # підтверджуємо всі зміни в БД

    # сповіщаємо всіх учасників кімнати що чат видалено
    socketio.emit("chat_deleted", {"groupId": group_id}, to=f"room_{group_id}")

    # Повертаємо підтвердження — JS отримає { ok: true }
    return flask.jsonify({"ok": True}), 200


@main_page.route("/my_chat", methods=["GET"])
@flask_login.login_required
def my_chat():
    # Шукаємо чат де поточний юзер є власником
    group = Group.query.filter_by(owner_id=flask_login.current_user.id).first()
    if group:
        # Чат знайдено — повертаємо його дані
        return flask.jsonify({"id": group.id, "name": group.group_name})
    # Чату немає — повертаємо порожній об'єкт
    # JS перевірить: if (data.id) — і нічого не покаже
    return flask.jsonify({}), 200


@main_page.route("/search_chats", methods=["GET"])
@flask_login.login_required
def search_chats():
    # Беремо параметр q з URL: /search_chats?q=текст
    query = flask.request.args.get("q", "").strip()
    if not query:
        # Порожній запит — повертаємо порожній масив
        return flask.jsonify([])

    # ilike — пошук без урахування регістру
    # f"%{query}%" — % означає "будь-які символи до і після"
    # наприклад query="ча" знайде "Мій чат", "чат друзів" і т.д.
    results = Group.query.filter(Group.group_name.ilike(f"%{query}%")).all()
    
    # Перетворюємо список об'єктів Group в список словників для JSON
    # JS отримає: [{ id: 1, name: "..." }, { id: 2, name: "..." }]
    return flask.jsonify([{
        "id": g.id, 
        "name": g.group_name
    } for g in results])


# <int:chat_id> — Flask автоматично бере id з URL і передає в функцію як int
# наприклад /join_chat/5 → chat_id = 5
@main_page.route("/join_chat/<int:chat_id>", methods=["POST"])
@flask_login.login_required
def join_chat(chat_id):
    # Шукаємо чат по id
    group = Group.query.get(chat_id)
    if not group:
        return flask.jsonify({"error": "not_found"}), 404

    # Перевіряємо чи юзер вже є учасником цього чату
    already = UserGroup.query.filter_by(user_id=flask_login.current_user.id, group_id=chat_id).first()
    if already:
        # Вже учасник — повертаємо ok але з флагом already_member
        return flask.jsonify({"ok": True, "already_member": True})

    # Юзер ще не в чаті — створюємо запис в UserGroup
    member = UserGroup(user_id=flask_login.current_user.id, group_id=chat_id)
    DATABASE.session.add(member)
    DATABASE.session.commit()

    return flask.jsonify({
        "ok": True
    }), 200

@main_page.route("/logout")
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login.render_login'))

@main_page.route('/chats/<int:chat_id>/')
@flask_login.login_required
def chat_page(chat_id):
    chat = Group.query.get_or_404(chat_id)
    messages = Message.query.filter_by(group_id=chat_id).order_by(Message.timestamp).all()
    return flask.render_template(
        'particles/chat_room.html', 
        chat=chat, 
        messages=messages
    )

# Маршрут для отримання списку всіх чатів з останніми повідомленнями
# Викликається при завантаженні сторінки з result.js
@main_page.route("/get_chats", methods=["GET"])
@flask_login.login_required
def get_chats():
    # Отримуємо всі групи з БД
    # chats = Group.query.all()

    # беремо тільки чати де поточний юзер є учасником
    user_groups = UserGroup.query.filter_by(user_id=flask_login.current_user.id).all()
    group_ids = [ug.group_id for ug in user_groups]
    chats = Group.query.filter(Group.id.in_(group_ids)).all()

    result = []
    for g in chats:
        # Шукаємо останнє повідомлення цієї групи
        # order_by(desc) — сортуємо від новіших до старіших, .first() — беремо перше (найновіше)
        last_msg = Message.query.filter_by(group_id=g.id).order_by(Message.timestamp.desc()).first()
        result.append({
            "id": g.id,
            "name": g.group_name,
            # якщо повідомлення є — беремо текст, інакше порожній рядок
            "last_message": last_msg.text if last_msg else "",
            # якщо повідомлення є — беремо час у форматі ISO (наприклад "2024-01-15T14:30:00")
            # JS функція timeAgo() перетворить це в "5m ago" і т.д.
            "last_time": last_msg.timestamp.isoformat() if last_msg else ""
        })
    # Повертаємо список словників у форматі JSON
    return flask.jsonify(result)


# Маршрут для отримання всіх повідомлень конкретного чату
# Викликається коли юзер клікає на чат — fetch(`/get_messages/${groupId}`) в chat.js
@main_page.route("/get_messages/<int:group_id>", methods=["GET"])
@flask_login.login_required
def get_messages(group_id):
    # Отримуємо всі повідомлення групи, відсортовані від старіших до новіших
    messages = Message.query.filter_by(group_id=group_id).order_by(Message.timestamp).all()
    return flask.jsonify([{
        "text": m.text,
        # якщо username заповнений — показуємо його, інакше показуємо email
        "author": m.author.username or m.author.email,
        "user_id": m.user_id,
        # форматуємо час у вигляді 09:24 AM / 02:30 PM
        "time": m.timestamp.strftime('%I:%M %p'),
    } for m in messages])

@main_page.route('/chats/<int:chat_id>/leave', methods=['POST'])
@flask_login.login_required
def leave_chat(chat_id):
    member = UserGroup.query.filter_by(group_id=chat_id, user_id=flask_login.current_user.id).scalar()
    if member:
        DATABASE.session.delete(member)
        DATABASE.session.commit()
    return flask.redirect(flask.url_for('main_page.main'))

# Маршрут для отримання списку учасників конкретного чату
# Викликається з JS коли юзер відкриває чат — fetch(`/get_members/${groupId}`)
@main_page.route("/get_members/<int:group_id>", methods=["GET"])
@flask_login.login_required
def get_members(group_id):
    # знаходимо групу по id — якщо немає повертаємо 404
    group = Group.query.get_or_404(group_id)

    all_users = len(group.users)
    
    # автоматично додаємо поточного юзера як учасника, якщо його ще немає
    # already = UserGroup.query.filter_by(user_id=flask_login.current_user.id, group_id=group_id).first()
    # if not already:
    #     new_member = UserGroup(user_id=flask_login.current_user.id, group_id=group_id)
    #     DATABASE.session.add(new_member)
    #     DATABASE.session.commit()

    count_online_users = 0
    for user in group.users:
        if user.id in online_users:
            count_online_users += 1

    # повертаємо список учасників у форматі JSON
    # для кожного юзера — name (username або email якщо username не заповнений)
    result = []
    for user in group.users:
        result.append({
            "id": user.id,
            "name": user.username or user.email,
            "email": user.email,
            "is_owner": user.id == group.owner_id,
            "is_online": user.id in online_users, # чи є в словнику
            "all_users": all_users,
            "count_online_user": count_online_users,
        })
    return flask.jsonify(result)

@main_page.route("/get_user/<int:user_id>", methods=["GET"])
@flask_login.login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return flask.jsonify({
        "name": user.username or user.email,
        "email": user.email,
        "birth_date": user.birth_date or "",
        "gender": user.gender or "",
    })