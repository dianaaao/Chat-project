from .settings import app
from home_app.apps import *

app.register_blueprint(blueprint = registration)
app.register_blueprint(blueprint = login)                    
app.register_blueprint(blueprint = main_page)

from .db import *
from .login import login_manager

login_manager.login_view = "login.render_login"