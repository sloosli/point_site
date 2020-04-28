from flask_wtf import FlaskForm
from flask import flash
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.constants import Access, access_desc
from app.models import Mentor, Discipline, Group


class MentorForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(),
                                                              EqualTo('password')])
    access_levels = SelectField('Уровень доступа', validators=[DataRequired()], coerce=int)
    disciplines = SelectField('Предмет', coerce=int)
    submit = SubmitField('Добавить')

    def __init__(self, current_user=None, original_username='', *args, **kwargs):
        super(MentorForm, self).__init__(*args, **kwargs)

        self.original_username = original_username
        self.access_levels.choices = sorted(filter(lambda x: x[0] < \
            current_user.access_level if current_user else 0,
                                            access_desc.items()))

        self.disciplines.choices = [(t.id, t.name)
                                    for t in Discipline.query.order_by(Discipline.name).all()]
        if current_user and\
                current_user.access_level == Access.UP_MENTOR:
            self.disciplines.choices = [(current_user.discipline_id, current_user.discipline.name)]

    def validate_username(self, username):
        if username.data != self.original_username:
            user = Mentor.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Пожалуйста выберите другое имя пользователя')

    def validate_disciplines(self, disciplines):
        if self.access_levels.data in [Access.MENTOR, Access.UP_MENTOR] and \
                disciplines.data is None:
            raise ValidationError('Пожалуйста, укажите предмет для наставника')


class ChangeMentorForm(MentorForm):
    password = PasswordField('Новый пароль')
    password2 = PasswordField('Повторите пароль', validators=[EqualTo('password')])
    submit = SubmitField('Изменить')

    def __init__(self, current_user, user, *args, **kwargs):
        kwargs['first_name'] = user.first_name or 'Имя'
        kwargs['last_name'] = user.last_name or 'Фамилия'
        kwargs['username'] = user.username
        kwargs['access_levels'] = user.access_level
        kwargs['disciplines'] = user.discipline.id if user.discipline else None

        super(ChangeMentorForm, self).__init__(current_user=current_user,
                                               original_username=user.username,
                                               *args, **kwargs)
        self.password.label.text = 'Новый пароль'
        self.submit.label.text = 'Изменить'


class ChangeSelfForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Новый пароль')
    password2 = PasswordField('Повторите пароль', validators=[EqualTo('password')])
    submit = SubmitField('Изменить')

    def __init__(self, user, *args, **kwargs):
        kwargs['first_name'] = user.first_name or 'Имя'
        kwargs['last_name'] = user.last_name or 'Фамилия'
        kwargs['username'] = user.username
        self.original_username = user.username

        super(ChangeSelfForm, self).__init__(*args, **kwargs)

        self.password.label.text = 'Новый пароль'
        self.submit.label.text = 'Изменить'

    def validate_username(self, username):
        if username.data != self.original_username:
            user = Mentor.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Пожалуйста выберите другое имя пользователя')


class GroupMentorForm(FlaskForm):
    groups = SelectField('Группа', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Добавить')

    def __init__(self, user, *args, **kwargs):
        super(GroupMentorForm, self).__init__(*args, **kwargs)
        group_ids = user.groups.with_entities(Group.id)
        self.groups.choices = [(t.id, t.name) for t in
                               Group.query.filter(
                                   Group.id.notin_(group_ids),
                                   Group.discipline_id == user.discipline_id
                               ).all()]

    def validate_groups(self, groups):
        group = Group.query.filter_by(id=groups.data).first()
        if group is None:
            raise ValidationError('Нет такой группы')