from flask import Blueprint

bp = Blueprint('disciplines', __name__)

from app.disciplines import routes
