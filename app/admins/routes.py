from flask import render_template, flash, redirect, url_for, request, abort, g
from flask_login import current_user, login_required
from app import app, db
from app.models import Mentor, AccessLevel, Discipline
from app.admins import bp
from app.admins.forms import MentorForm, ChangeMentorForm
from app.constants import Access


def get_user(username):
    if username != current_user.username:
        user = Mentor.query.filter_by(username=username).first_or_404()
        if user.access_level >= current_user.access_level:
            abort(404)
    else:
        user = current_user

    return user


@bp.before_request
def before_request():
    if current_user.is_authenticated and \
            current_user.access_level < Access.ADMIN:
        return redirect(url_for('main.index'))


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/mentor_list', methods=['GET', 'POST'])
@login_required
def mentor_list():
    form = MentorForm(current_user.access_level)
    page = request.args.get('page', 1, type=int)

    if form.validate_on_submit():
        # noinspection PyArgumentList
        new_mentor = Mentor(username=form.username.data,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            access_level=form.access_levels.data)
        new_mentor.set_password(form.password.data)
        if new_mentor.access_level in [Access.MENTOR, Access.UP_MENTOR]:
            new_mentor.discipline_id = form.disciplines.data

        db.session.add(new_mentor)
        db.session.commit()
        flash('%s %s добавлен' % (new_mentor.access.name, new_mentor.username))
        return redirect(url_for('admins.mentor_list', page=page))

    data = Mentor.query.filter(
        # Администраторов может добавлять только главный администратор
        Mentor.access_level < current_user.access_level
    ).order_by(
        Mentor.username
    ).paginate(
        page, app.config['MENTORS_PER_PAGE'], False
    )
    g.url_for = 'admins.mentor_list'

    return render_template('data_list.html', form=form,
                           data=data, title='Список менторов')


@bp.route('/mentor', methods=['GET', 'POST'])
@login_required
def self_mentor():
    return redirect(url_for('admins.mentor', username=current_user.username))


@bp.route('/mentor/<username>', methods=['GET', 'POST'])
@login_required
def mentor(username):
    user = get_user(username)
    form = ChangeMentorForm(current_access=current_user.access_level,
                            user=user)

    if user.id == current_user.id:
        form.access_levels.flags.not_need = True
        form.disciplines.flags.not_need = True

    if form.validate_on_submit():
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        if form.password.data:
            user.set_password(form.password.data)

        if form.access_levels.data < current_user.access_level and \
                user.id != current_user.id:
            user.access_level = form.access_levels.data

        if form.access_levels.data in [Access.MENTOR, Access.UP_MENTOR]:
            user.discipline_id = form.disciplines.data

        db.session.commit()
        flash('%s %s Изменен' % (user.access.name, user.username))

        return redirect(url_for('admins.mentor', username=user.username))

    return render_template('admins/mentor_page.html', form=form,
                           mentor=user, title=user.username)


@bp.route('/mentor/remove_mentor/<username>')
def remove_mentor(username):
    user = get_user(username)

    if user.id != current_user.id:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('admins.mentor_list'))
