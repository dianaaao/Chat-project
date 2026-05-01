import flask_sqlalchemy, flask_migrate, os
from .settings import app

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

DATABASE = flask_sqlalchemy.SQLAlchemy(app = app)


MIGRATE = flask_migrate.Migrate(
    app = app,
    db = DATABASE,
    directory = os.path.abspath(os.path.join(__file__, "..", "migrations"))
)