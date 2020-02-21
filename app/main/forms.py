from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired
from app.models import Student, Group, Discipline


class StudentForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    vk_id = IntegerField('ID Вконтакте', validators=[DataRequired()])

    submit = SubmitField('Добавить')

    def __init__(self, original_vk_id='', *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.original_vk_id = original_vk_id

    def validate_vk_id(self, vk_id):
        if vk_id.data != self.original_vk_id:
            user = Student.query.filter_by(vk_id=vk_id.data).first()
            if user is not None:
                raise ValidationError('Этот id уже зарегестрирован в системе, проверьте правильность ввода')


class ChangeStudentForm(StudentForm):
    submit = SubmitField('Изменить')

    def __init__(self, student, *args, **kwargs):
        kwargs['first_name'] = student.first_name or 'Имя'
        kwargs['last_name'] = student.last_name or 'Фамилия'
        kwargs['vk_id'] = student.vk_id

        super(ChangeStudentForm, self).__init__(original_vk_id=student.vk_id,
                                                *args, **kwargs)
        self.submit.label.text = 'Изменить'


class GroupForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    disciplines = SelectField('Предмет', coerce=int)
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.disciplines.choices = [(t.id, t.name)
                                    for t in Discipline.query.order_by(Discipline.name).all()]

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        if group is not None:
            raise ValidationError('Группа с таким названием уже существует')
