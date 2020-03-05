from flask import Blueprint

bp = Blueprint('communities', __name__)

from app.communities import routes
