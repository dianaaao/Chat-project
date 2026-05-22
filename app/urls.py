from home_app.apps import *
from home_app.views import *


registration.add_url_rule(
    rule = '/',
    view_func = render_registration,
    methods = ["GET", "POST"],
    registration = True
)

login.add_url_rule(
    rule = "/login",
    view_func = render_login,
    methods = ["GET", "POST"],
    login = True
)

success_page.add_url_rule(
    rule = "/success_page",
    view_func = render_success_page,
    success_page = True,
)

main_page.add_url_rule(
    rule = "/main_page",
    view_func = render_home,
    methods = ["GET", "POST"],
    main_page = True,
)