from app.db import DATABASE
import flask_login

class User(DATABASE.Model, flask_login.UserMixin):
    id = DATABASE.Column(DATABASE.Integer, primary_key = True)
    
    first_name = DATABASE.Column(DATABASE.String(255))
    last_name = DATABASE.Column(DATABASE.String(255))
    email = DATABASE.Column(DATABASE.String(255), nullable = False, unique = True)
    password_hash = DATABASE.Column(DATABASE.String(255))
    avatar_path = DATABASE.Column(DATABASE.String(255))
    gender = DATABASE.Column(DATABASE.String(255))
    birth_date = DATABASE.Column(DATABASE.String(255))