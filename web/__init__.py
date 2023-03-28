from datetime import timedelta
from flask import Flask
from pymongo import MongoClient

# render secret to hide db password
dbpass = "0h4ceylo58Ks9lKY"
ggpass = "svisqumhrixagvbc"
"""
with open("dbpassword", "r") as file:
    dbpass = file.readline()
with open("ggpassword", "r") as file:
    ggpass = file.readline()
"""

# e-mail connection
ggemail = "projectstinn@gmail.com"

# mongo connection
client = MongoClient(f"mongodb+srv://admin:{dbpass}@cluster0.qrgpqol.mongodb.net/?retryWrites=true&w=majority")
db = client.db
account_db = db.account
exchange_db = db.exchange
transaction_db = db.transaction
balance_db = db.balance

def create_app():
    app = Flask(__name__, template_folder="../front/templates", static_folder="../front/static")

    # app configuration
    app.config["SECRET_KEY"] = "stintest"
    app.permanent_session_lifetime = timedelta(minutes=5)

    # blueprint for routes
    from .routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint, url_prefix="/")

    return app