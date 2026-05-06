import flask_login, dotenv, os
from .settings import app
from home_app.models import User

dotenv.load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

login_manager = flask_login.LoginManager()
login_manager.init_app(app = app)

@login_manager.user_loader
def get_user(user_id):
    return User.query.get(user_id)

