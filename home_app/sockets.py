import flask, flask_login, flask_socketio
from datetime import timezone, timedelta

from app.settings import socketio
from app.db import DATABASE
from .apps import online_users
from .models import Message, Group, UserGroup


# часовий пояс — Україна (UTC+2 або +3 залежно від DST)
LOCAL_TZ = timezone(timedelta(hours=3))
# словник { group_id: set(user_id1, user_id2, ...) }
# зберігає хто вже заходив в яку кімнату за поточну роботу сервера
# users_in_room = {}

@socketio.on("connect")
def handle_connect():
    print("Клієнт підключився")

    if flask_login.current_user.id not in online_users.keys():
        online_users[flask_login.current_user.id] = set()
        socketio.emit("user_status_online", {"user_id": flask_login.current_user.id})


    online_users[flask_login.current_user.id].add(flask.request.sid)

    print("ONLINE:", flask_login.current_user.id)
    

@socketio.on("disconnect")
def handle_disconnect():
    print("Клієнт відключився")

    if flask_login.current_user.id in online_users.keys():
        online_users[flask_login.current_user.id].discard(flask.request.sid) 

        print("OFFLINE:", flask_login.current_user.id)

        if not online_users[flask_login.current_user.id]:
            del online_users[flask_login.current_user.id]
           
            socketio.emit("user_status_offline", {"user_id": flask_login.current_user.id})

@socketio.on("join_room")
def handle_join_room(data):
    group_id = data["groupId"]
    user_id = flask_login.current_user.id

    group = Group.query.get(group_id)
    username = flask_login.current_user.username or flask_login.current_user.email

    if group:
        flask_socketio.join_room(f'room_{group.id}')  # прибрали перевірку membership

    # перевіряємо чи юзер вже заходив у цю кімнату раніше
        # if group_id not in users_in_room:
        #     users_in_room[group_id] = set()

        # is_first_time = user_id not in users_in_room[group_id]

        # if is_first_time:
        #     users_in_room[group_id].add(user_id)
        # шукаємо запис учасника в БД
        member = UserGroup.query.filter_by(user_id=user_id, group_id=group_id).first()

        if member and not member.has_joined:
            member.has_joined = True
            DATABASE.session.commit()

            # показуємо повідомлення тільки при справді першому вході
            flask_socketio.emit(
                "system_message",
                {"text": f"{username} приєднався до чату"},
                to=f'room_{group.id}'
            )

            # "join_room",
            # {
            #     "room": f'room_{group.id}',
            #     "message": "Підключився клієнт в кімнату",
            #     "username": username
            # }
        
        # сповіщаємо всіх в кімнаті що список учасників оновився
        flask_socketio.emit(
            "members_updated",
            {"groupId": group_id},
            to=f'room_{group.id}'
        )

@socketio.on("leave_room")
def handle_leave_room(data):
    group_id = data["groupId"]
    user_id = flask_login.current_user.id

    group = Group.query.get(group_id)
    username = flask_login.current_user.username or flask_login.current_user.email

    if group:
        flask_socketio.leave_room(f'room_{group.id}')

        # видаляємо юзера зі словника — щоб при наступному вході знову показалось "приєднався"
        # if group_id in users_in_room:
        #     users_in_room[group_id].discard(user_id)

        # скидаємо прапорець — щоб при наступному вході знову показалось повідомлення
        member = UserGroup.query.filter_by(user_id=user_id, group_id=group_id).first()
        if member:
            member.has_joined = False
            DATABASE.session.commit()

        flask_socketio.emit(
            "system_message",
            {
                "text": f"{username} покинув чат",
            },
            # "leave_room",
            # {
            #     "room": f'room_{group.id}',
            #     "message": "Клієнт покинув кімнату",
            #     "username": username
            # },
            to=f'room_{group.id}'
        )

@socketio.on("send_message")
def handle_send_message(data):
    group_id = data["groupId"]
    text = data["text"]

    group = Group.query.get(group_id)

    if group and text:
        msg = Message(
            text=text,
            user_id=flask_login.current_user.id,
            group_id=group_id
        )
        DATABASE.session.add(msg)
        DATABASE.session.commit()

        # беремо username або email якщо username не заповнений
        author = flask_login.current_user.username or flask_login.current_user.email

        flask_socketio.emit(
            "new_message",
            {
                "text": text,
                "author": author,
                "userId": flask_login.current_user.id,
                "avatar_url": f"/main_page/static/images/avatars/{flask_login.current_user.avatar_path}" if flask_login.current_user.avatar_path else None,
                "time": msg.timestamp.replace(tzinfo=timezone.utc).astimezone(LOCAL_TZ).strftime('%I:%M %p')
            },
            to=f'room_{group.id}'
        )

@socketio.on("switch_room")
def handle_switch_room(data):
    group_id = data["groupId"]
    group = Group.query.get(group_id)
    if group:
        flask_socketio.leave_room(f'room_{group.id}')


        



