from flask import render_template, flash, redirect, url_for, g
from flask_login import current_user, login_required
from app import db
from app.models import Mentor
from app.main import bp
from app.constants import Access, navs


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
    return render_template('base.html', title='Группы')


@bp.route('/student_list', methods=['GET', 'POST'])
@login_required
def student_list():
    if current_user.access_level in [Access.MENTOR, Access.UP_MENTOR]:
        return redirect(url_for('main.group_list'))
    return render_template('base.html', title='Студенты')


@bp.route('/student/<student_id>', methods=['GET', 'POST'])
@login_required
def student(student_id):
    return 'pass'
