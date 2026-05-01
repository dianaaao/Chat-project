from .settings import app
from home_app.apps import *

# app.register_blueprint(blueprint = main_page)
app.register_blueprint(blueprint = registration)
app.register_blueprint(blueprint = login)                    

from .db import *