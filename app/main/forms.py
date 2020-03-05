from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired
from app.models import Student, Group, Discipline, Theme



class GroupForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    disciplines = SelectField('Предмет', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, group_name='', *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.group_name = group_name
        self.disciplines.choices = [(t.id, t.name)
                                    for t in Discipline.query.order_by(Discipline.name).all()]

    def validate_name(self, name):
        if self.group_name != name.data:
            group = Group.query.filter_by(name=name.data).first()
            if group is not None:
                raise ValidationError('Группа с таким названием уже существует')


class ChangeGroupForm(GroupForm):
    submit = SubmitField('Изменить')

    def __init__(self, group, *args, **kwargs):
        kwargs['name'] = group.name

        super(ChangeGroupForm, self).__init__(group_name=group.name,
                                              *args, **kwargs)
        self.submit.label.text = 'Изменить'


class DisciplineRecordForm(FlaskForm):
    themes = SelectField('Тема', validators=[DataRequired()], coerce=int)
    amount = IntegerField('Баллы')
    submit = SubmitField('Добавить')

    def __init__(self, themes, *args, **kwargs):
        super(DisciplineRecordForm, self).__init__(*args, **kwargs)
        self.themes.choices = [(theme.id, theme.discipline.name + ' ' +theme.name)
                               for theme in themes]


class ReferRecordForm(FlaskForm):
    referal = StringField('Приглашенный', validators=[DataRequired()], coerce=int)


