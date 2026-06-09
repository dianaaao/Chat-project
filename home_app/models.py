from app.db import DATABASE
import flask_login
from datetime import datetime, timezone

class User(DATABASE.Model, flask_login.UserMixin):
    id = DATABASE.Column(DATABASE.Integer, primary_key = True)
    
    first_name = DATABASE.Column(DATABASE.String(255), nullable = True)
    last_name = DATABASE.Column(DATABASE.String(255), nullable = True)
    email = DATABASE.Column(DATABASE.String(255), nullable = False, unique = True)
    password_hash = DATABASE.Column(DATABASE.String(255))
    avatar_path = DATABASE.Column(DATABASE.String(255))
    username = DATABASE.Column(DATABASE.String(255), unique = True)
    gender = DATABASE.Column(DATABASE.String(255))
    birth_date = DATABASE.Column(DATABASE.String(255))

    is_verified = DATABASE.Column(DATABASE.Boolean, default = False)
    groups = DATABASE.relationship("Group", secondary = "user_group", back_populates = "users")
    
class UserGroup(DATABASE.Model):
    id = DATABASE.Column(DATABASE.Integer, primary_key = True)
    
    user_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("user.id"))
    group_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("group.id"))

class Group(DATABASE.Model):
    id = DATABASE.Column(DATABASE.Integer, primary_key = True)

    group_name = DATABASE.Column(DATABASE.String(255))
    owner_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("user.id"), nullable = True) 
    
    users = DATABASE.relationship("User", secondary = "user_group", back_populates = "groups")
    
class Message(DATABASE.Model):
    id = DATABASE.Column(DATABASE.Integer, primary_key = True)

    text = DATABASE.Column(DATABASE.Text, nullable = False)
    time_stamp = DATABASE.Column(DATABASE.DateTime, default = datetime.now(timezone.utc))

    user_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("user.id"))
    group_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("group.id"))


    author = DATABASE.relationship("User", backref="messages")




