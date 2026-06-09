import flask, os, flask_socketio


app = flask.Flask(
    import_name = "app",
    static_folder = 'static',
    static_url_path = '/static',
    template_folder = 'templates',
    instance_path = os.path.abspath(os.path.join(__file__, '..', 'instance')),
)

socketio = flask_socketio.SocketIO(app = app)
