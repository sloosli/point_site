from flask import render_template, flash, redirect, url_for, g, request
from flask_login import current_user, login_required
from app import app, db
from app.models import Student, Group
from app.main import bp
from app.main.forms import StudentForm, ChangeStudentForm, GroupForm
from app.constants import Access, navs


def get_user(student_id):
    user = Student.query.filter_by(id=student_id).first_or_404()
    return user


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
    ).paginate(
        page, app.config['GROUPS_PER_PAGE'], False
    )
    g.url_for = 'main.group_list'

    return render_template('data_list.html', form=form,
                           title='Список групп', data=groups)


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
    if current_user.access_level in [Access.ADMIN, Access.SUPER_ADMIN]:
        form = ChangeStudentForm(user)

        if form.validate_on_submit():
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.vk_id = form.vk_id.data

            db.session.commit()
            flash('Запись тудента %s изменена' % user.username)

            return redirect(url_for('main.student', student_id=user.id))

    return render_template('main/student_page.html', form=form,
                           student=user, title=user.username)


@bp.route('/student/remove/<student_id>')
def remove_student(student_id):
    if current_user.access_level not in [Access.SUPER_ADMIN, Access.ADMIN]:
        redirect(url_for('main.index'))

    user = get_user(student_id)

    if user.id != current_user.id:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('main.student_list'))
