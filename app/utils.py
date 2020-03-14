from functools import wraps
from flask import redirect, url_for, abort
from flask_login import current_user
from app.models import Mentor, Student, Group, DisciplinePointRecord, Theme
from app.constants import Access


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user is None or current_user.is_anonymous or \
                current_user.access_level not in [Access.ADMIN, Access.SUPER_ADMIN]:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def angel_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user is None or current_user.is_anonymous or \
                current_user.access_level not in [Access.ANGEL, Access.ADMIN, Access.SUPER_ADMIN]:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def get_mentor(username):
    if username != current_user.username:
        user = Mentor.query.filter_by(username=username).first_or_404()
        if user.access_level >= current_user.access_level:
            abort(404)
    else:
        user = current_user

    return user


def get_student(student_id):
    user = Student.query.filter_by(id=student_id).first_or_404()
    return user


def get_group(group_id):
    group = Group.query.filter_by(id=group_id).first_or_404()
    return group


def is_admin(user):
    return current_user.access_level in [Access.ADMIN, Access.SUPER_ADMIN]


def get_discipline_records(student):
    if current_user.access_level == Access.HAWK:
        return None

    discipline_records = student.discipline_records
    if current_user.access_level in [Access.MENTOR, Access.UP_MENTOR]:
        theme_ids = current_user.discipline.themes.with_entities(Theme.id)
        discipline_records.filter(
            DisciplinePointRecord.theme_id.in_(theme_ids))

    return discipline_records
