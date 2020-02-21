from flask import render_template, flash, redirect, url_for, g, request
from flask_login import current_user, login_required
from app import app, db
from app.models import Student, Group
from app.main import bp
from app.main.forms import (StudentForm, ChangeStudentForm,
                            GroupForm, ChangeGroupForm, GroupStudentForm)
from app.constants import Access, navs
from app.admins.routes import admin_required


def get_user(student_id):
    user = Student.query.filter_by(id=student_id).first_or_404()
    return user


def get_group(group_id):
    group = Group.query.filter_by(id=group_id).first_or_404()
    return group


@bp.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        g.navs = navs[current_user.access_level]


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.access_level != Access.HAWK:
        return redirect(url_for('main.group_list'))
    return redirect(url_for('main.student_list'))


@bp.route('/group_list', methods=['GET', 'POST'])
@login_required
def group_list():
    if current_user.access_level == Access.HAWK:
        return redirect(url_for('main.student_list'))

    page = request.args.get('page', 1, type=int)
    form = None
    if current_user.access_level in [Access.ADMIN, Access.SUPER_ADMIN]:
        form = GroupForm()
        if form.validate_on_submit():
            # noinspection PyArgumentList
            new_group = Group(name=form.name.data, discipline_id=form.disciplines.data)

            db.session.add(new_group)
            db.session.commit()
            flash('Группа %s добавлена' % new_group.name)
            return redirect(url_for('main.group_list', page=page))

    groups = Group.query.order_by(
        Group.name
    )
    if current_user.access_level == Access.UP_MENTOR:
        groups = groups.filter_by(discipline_id=current_user.discipline_id)

    if current_user.access_level == Access.MENTOR:
        groups = current_user.groups

    groups = groups.paginate(
        page, app.config['GROUPS_PER_PAGE'], False
    )
    g.url_for = 'main.group_list'

    return render_template('data_list.html', form=form,
                           title='Список групп', data=groups)


@bp.route('/group/<group_id>', methods=['GET', 'POST'])
@login_required
def group(group_id):
    current_group = get_group(group_id)
    if current_user.access_level in [Access.MENTOR, Access.UP_MENTOR] and \
            current_user.discipline_id != current_group.discipline_id:
        return redirect(url_for('main.index'))

    form = None
    if current_user.access_level in [Access.ADMIN, Access.SUPER_ADMIN]:
        form = ChangeGroupForm(current_group)

        if form.validate_on_submit():
            current_group.name = form.name.data

            db.session.commit()
            flash('Запись группы %s изменена' % current_group.name)

            return redirect(url_for('main.group', group_id=current_group.id))

    return render_template('main/group_page.html', form=form,
                           group=current_group, title=current_group.name)


@bp.route('/group/remove/<group_id>')
@login_required
@admin_required
def remove_group(group_id):
    group = get_group(group_id)

    db.session.delete(group)
    db.session.commit()

    return redirect(url_for('main.group_list'))


@bp.route('/student_list', methods=['GET', 'POST'])
@login_required
def student_list():
    if current_user.access_level in [Access.MENTOR, Access.UP_MENTOR]:
        return redirect(url_for('main.group_list'))

    page = request.args.get('page', 1, type=int)
    form = None
    if current_user.access_level in [Access.ADMIN, Access.SUPER_ADMIN]:
        form = StudentForm()
        if form.validate_on_submit():
            # noinspection PyArgumentList
            new_student = Student(first_name=form.first_name.data,
                                  last_name=form.last_name.data,
                                  vk_id=form.vk_id.data)

            db.session.add(new_student)
            db.session.commit()
            flash('Студент %s добавлен' % (
                    new_student.last_name + ' ' + new_student.first_name))
            return redirect(url_for('main.student_list', page=page))

    students = Student.query.order_by(
        Student.last_name, Student.first_name
    ).paginate(
        page, app.config['STUDENTS_PER_PAGE'], False
    )
    g.url_for = 'main.student_list'
    return render_template('data_list.html', form=form,
                           title='Список студентов', data=students)


@bp.route('/student/<student_id>', methods=['GET', 'POST'])
@login_required
def student(student_id):
    user = get_user(student_id)
    form = None
    group_form = None
    request_form = request.form

    if current_user.access_level in [Access.ADMIN, Access.SUPER_ADMIN]:

        form = ChangeStudentForm(user)
        group_form = GroupStudentForm(user)

        if not request_form.get('submit', None):
            return render_template('main/student_page.html', group_form=group_form,
                                   form=form, student=user, title=user.username)

        if request_form['submit'] == 'Изменить' and form.validate_on_submit():
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.vk_id = form.vk_id.data

            db.session.commit()
            flash('Запись студента %s изменена' % user.username)

            return redirect(url_for('main.student', student_id=user.id))

        if request_form['submit'] == 'Добавить' and group_form.validate_on_submit():
            current_group = Group.query.filter_by(id=group_form.groups.data).first()
            user.add_group(current_group)
            db.session.commit()

            flash("Группа %s добавлена студенту %s" % (current_group.name, user.username))

            return redirect(url_for('main.student', student_id=user.id))

    return render_template('main/student_page.html', group_form=group_form,
                           form=form, student=user, title=user.username)


@bp.route('/student/remove/<student_id>')
@login_required
@admin_required
def remove_student(student_id):
    user = get_user(student_id)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('main.student_list'))
