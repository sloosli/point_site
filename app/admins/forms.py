from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Mentor
from app.constants import Access


class MentorForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(),
                                                              EqualTo('password')])
    access_levels = SelectField('Уровень доступа', validators=[DataRequired()], coerce=int)
    disciplines = SelectField('Предмет', coerce=int)

    submit = SubmitField('Добавить')


    def validate_username(self, username):
        user = Mentor.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста выберите другое имя пользователя')

    def validate_disciplines(self, disciplines):
        if self.access_levels.data in [Access.MENTOR, Access.UP_MENTOR] and \
           disciplines.data is None:
            raise ValidationError('Пожалуйста, укажите предмет для наставника')
