from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from app.models import VkGroup


class VkGroupform(FlaskForm):
    pass
