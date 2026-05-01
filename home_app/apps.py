import flask

# main_page = flask.Blueprint(
#     name = "main_page",
#     import_name = __name__,
#     static_folder = "static",
#     template_folder = "templates",
#     static_url_path = "/static",
# )

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
    static_url_path = '/login/static',
    template_folder = 'templates',
)