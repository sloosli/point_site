from flask import render_template, flash, redirect, url_for, g, request
from flask_login import current_user, login_required
import vk_api
from wtforms.validators import ValidationError
from app import app, db
from app.students import bp
from app.students.forms import StudentForm, ChangeStudentForm, GroupStudentForm
from app.constants import Access
from app.utils import admin_required, get_student, is_admin, get_vk_users_data
from app.models import Student, Group


@bp.route('/list', methods=['GET', 'POST'])
@login_required
def list():
    if current_user.access_level in [Access.MENTOR, Access.UP_MENTOR]:
        return redirect(url_for('main.group_list'))

    page = request.args.get('page', 1, type=int)
    form = None
    r_form = request.form
    if current_user.access_level > 3:
        form = StudentForm()
        if r_form.get('submit', None) and form.validate_on_submit():
            # noinspection PyArgumentList
            new_student = Student(first_name=form.first_name.data,
                                  last_name=form.last_name.data,
                                  vk_id=form.vk_id.data)

            db.session.add(new_student)
            db.session.commit()
            flash('Студент %s добавлен' % (
                    new_student.last_name + ' ' + new_student.first_name))
            return redirect(url_for('students.list', page=page))

    students = Student.query.order_by(
        Student.last_name, Student.first_name
    )

    if r_form.get('search', None):
        if r_form.get('first_name', None):
            students = students.filter_by(first_name=r_form['first_name'].replace(' ', ''))
        if r_form.get('last_name', None):
            students = students.filter_by(last_name=r_form['last_name'].replace(' ', ''))
        if r_form.get('_id', None):
            students = students.filter_by(vk_id=r_form['_id'].replace(' ', ''))

    students = students.paginate(
        page, app.config['STUDENTS_PER_PAGE'], False
    )

    g.url_for = 'students.list'
    return render_template('students/student_list.html', form=form,
                           title='Список студентов', data=students)


@bp.route('/id/<student_id>', methods=['GET', 'POST'])
@login_required
def student(student_id):
    user = get_student(student_id)
    form = None
    group_form = None
    request_form = request.form

    if is_admin(current_user):

        form = ChangeStudentForm(user)
        group_form = GroupStudentForm(user)

        if not request_form.get('submit', None):
            return render_template('students/student_page.html', group_form=group_form,
                                   form=form, student=user, title=user.username)

        if request_form['submit'] == 'Изменить' and form.validate_on_submit():
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.vk_id = form.vk_id.data

            db.session.commit()
            flash('Запись студента %s изменена' % user.username)

            return redirect(url_for('students.student', student_id=user.id))

        if request_form['submit'] == 'Добавить' and group_form.validate_on_submit():
            current_group = Group.query.filter_by(id=group_form.groups.data).first()
            user.add_group(current_group)
            db.session.commit()

            flash("Группа %s добавлена студенту %s" % (current_group.name, user.username))

            return redirect(url_for('students.student', student_id=user.id))

    return render_template('students/student_page.html', group_form=group_form,
                           form=form, student=user, title=user.username)


@bp.route('/multiple_add', methods=['POST'])
def multiple_add():
    r_form = request.form

    users = get_vk_users_data(r_form)
    if users is None:
        flash('Проверьте правильность id')
        return redirect(url_for('students.list'))

    for user in users:
        student = Student.query.filter_by(vk_id=user['id']).first()
        if student is not None:
            flash("Студет с id %s уже зарегистрирован в системе" % user['id'])
        else:
            student = Student(first_name=user['first_name'],
                              last_name=user['last_name'],
                              vk_id=user['id'])
            db.session.add(student)
            flash("Студент %s vk_id: %i Добавлен" % (student.username, student.vk_id))
    db.session.commit()

    return redirect(url_for('students.list'))


@bp.route('/remove/<student_id>')
@login_required
@admin_required
def remove(student_id):
    user = get_student(student_id)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('students.list'))
