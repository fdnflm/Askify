from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)
mail = Mail(app)
moment = Moment(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
