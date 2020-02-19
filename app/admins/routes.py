from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import app, db
from app.models import Mentor, AccessLevel, Discipline
from app.admins import bp
from app.admins.forms import MentorForm
from app.constants import Access


@bp.before_request
def before_request():
    if current_user.is_authenticated and \
            current_user.access_level < Access.ADMIN:
        return redirect(url_for('main.index'))


@bp.route('/mentor_list', methods=['GET', 'POST'])
@login_required
def mentor_list():
    form = MentorForm()
    form.access_levels.choices = [(t.id, t.name)
        for t in AccessLevel.query.filter(
            AccessLevel.id < current_user.access_level
        ).order_by(AccessLevel.id).all()]
    form.disciplines.choices = [(t.id, t.name)
        for t in Discipline.query.order_by(Discipline.name).all()]

    if form.validate_on_submit():
        # noinspection PyArgumentList
        new_mentor = Mentor(username=form.username.data,
                            access_level=form.access_levels.data)
        new_mentor.set_password(form.password.data)
        if new_mentor.access_level in [Access.MENTOR, Access.UP_MENTOR]:
            new_mentor.discipline_id = form.disciplines.data

        db.session.add(new_mentor)
        db.session.commit()
        flash('%s %s добавлен' % (new_mentor.access.name, new_mentor.username))
        return redirect(url_for('admins.mentor_list'))

    page = request.args.get('page', 1, type=int)
    data = Mentor.query.filter(
        # Администраторов может добавлять только главный администратор
        Mentor.access_level < current_user.access_level
    ).order_by(
        Mentor.username
    ).paginate(
        page, app.config['MENTORS_PER_PAGE'], False
    )

    return render_template('admins/mentor_list.html', form=form,
                           mentors=data.items, title='Список менторов')


@bp.route('/mentor/<username>')
@login_required
def mentor(username):
    return "pass"