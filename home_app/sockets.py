from app.settings import socketio
from app.db import DATABASE
from .models import Message, Group, UserGroup
import flask_login, flask_socketio

@socketio.on("connect")
def handle_connect():
    print("Клієнт підключився")

@socketio.on("disconnect")
def handle_disconnect():
    print("Клієнт відключився")

@socketio.on("join_room")
def handle_join_room(data):
    group_id = data["groupId"]

    group = Group.query.get(group_id)

    if group:
        flask_socketio.join_room(f'room_{group.id}')  # прибрали перевірку membership

        flask_socketio.emit(
            "join_room",
            {
                "room": f'room_{group.id}',
                "message": "Підключився клієнт в кімнату"
            },
            to=f'room_{group.id}'
        )

@socketio.on("leave_room")
def handle_leave_room(data):
    group_id = data["groupId"]

    group = Group.query.get(group_id)

    if group:
        flask_socketio.leave_room(f'room_{group.id}')

        flask_socketio.emit(
            "leave_room",
            {
                "room": f'room_{group.id}',
                "message": "Клієнт покинув кімнату"
            },
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
                "time": msg.timestamp.strftime('%I:%M %p')
            },
            to=f'room_{group.id}'
        )