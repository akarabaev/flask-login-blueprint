from flask import Flask, render_template
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

login = LoginManager(app)
login.login_view = 'login_bp.login'
login.login_message = 'Пожалуйста вначале войдите в систему'


from app import models


@login.user_loader
def load_user(id):
    return db.session.get(models.User, int(id))


@app.route('/')
def index():
    return render_template('index.html', current_user=current_user)


from .login import bp as login_bp
app.register_blueprint(login_bp)
