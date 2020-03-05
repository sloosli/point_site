from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'auth.login'
login.login_message = 'Вам необходимо войти, что бы увидеть эту страницу'

# I think there are too many blueprints
# but otherwise the code in routes is getting terrible
from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.main import bp as main_bp
app.register_blueprint(main_bp)

from app.admins import bp as admins_bp
app.register_blueprint(admins_bp, url_prefix='/mentor')

from app.disciplines import bp as disciplines_bp
app.register_blueprint(disciplines_bp, url_prefix='/discipline')

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.students import bp as students_bp
app.register_blueprint(students_bp, url_prefix='/student')

from app.communities import bp as communities_bp
app.register_blueprint(communities_bp, url_prefix='/communities')

from app import models
