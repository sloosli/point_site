from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from app.models import Theme, Discipline


class DisciplineForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def validate_name(self, name):
        discipline = Discipline.query.filter_by(name=name.data).first()
        if discipline is not None:
            raise ValidationError('Такой предмет уже существует')


class ThemeForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    max_points = IntegerField('Максимальный балл', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, discipline_id, *args, **kwargs):
        super(ThemeForm, self).__init__(*args, **kwargs)
        self.discipline_id = discipline_id

    def validate_name(self, name):
        theme = Theme.query.filter_by(
            discipline_id=self.discipline_id
        ).filter_by(name=name.data).first()
        if theme is not None:
            raise ValidationError('В этом предмете уже есть данная тема')
