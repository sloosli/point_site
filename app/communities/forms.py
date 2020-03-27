from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from app.models import VkGroup


class VkGroupForm(FlaskForm):
    token = StringField('Токен', validators=[DataRequired()])
    vk_id = IntegerField('Id вконтакте', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class VkGroupChangeForm(FlaskForm):
    message = StringField('Сообщение о баллах', validators=[DataRequired()])
    submit = SubmitField('Изменить')

    def __init__(self, message, *args, **kwargs):
        kwargs['message'] = message

        super(VkGroupChangeForm, self).__init__(*args, **kwargs)
