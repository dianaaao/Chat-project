import flask



registration = flask.Blueprint(
    name = "registration",
    import_name = __name__,
    static_folder = "static",
    template_folder = "templates",
    static_url_path = "/registration/static",
)

login = flask.Blueprint(
    name = 'login',
    import_name = __name__,
    static_folder = 'static',
    template_folder = 'templates',
    static_url_path = '/login/static',
)

main_page = flask.Blueprint(
    name = "main_page",
    import_name = __name__,
    static_folder = "static",
    template_folder = "templates",
    static_url_path = "/main_page/static",
)