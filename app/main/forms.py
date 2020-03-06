from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired
from app.models import Group, Discipline, ReferPointRecord



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
    amount = IntegerField('Баллы', default=0, validators=[DataRequired(message="Значение должно быть числом")])
    submit = SubmitField('Добавить')

    def __init__(self, themes, *args, **kwargs):
        super(DisciplineRecordForm, self).__init__(*args, **kwargs)
        self.themes.choices = [(theme.id, theme.discipline.name + ' ' + theme.name)
                               for theme in themes]

    def validate_amount(self, amount):
        if not self.amount.data or self.amount.data <= 0:
            raise ValidationError("Значение должно быть положительным")


class ReferRecordForm(FlaskForm):
    referal = IntegerField('Приглашенный', validators=[DataRequired(message="Значение должно быть числом")])
    amount = IntegerField('Баллы', default=100, validators=[DataRequired(message="Значение должно быть числом")])
    submit = SubmitField('Добавить')

    def validate_referal(self, referal):
        if not self.referal.data or self.referal.data <= 0:
            raise ValidationError("Значение должно быть положительным")
        record = ReferPointRecord.query.filter_by(refer_vk_id=referal.data).first()
        if record is not None:
            raise ValidationError("Этого ученика уже пригласил ученик %s id: %i" %
                                  (record.student.username, record.student.vk_id))

    def validate_amount(self, amount):
        if not self.amount.data or self.amount.data <= 0:
            raise ValidationError("Значение должно быть положительным")
