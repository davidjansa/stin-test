from datetime import timedelta
from flask import Flask

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # app configuration
    app.config["SECRET_KEY"] = "stintest"
    app.permanent_session_lifetime = timedelta(minutes=5)

    # blueprint for routes
    from .routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint, url_prefix="/")

    return app