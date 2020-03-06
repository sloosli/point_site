from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user
from app import app, db
from app.models import Mentor, Group
from app.admins import bp
from app.admins.forms import MentorForm, ChangeMentorForm, GroupMentorForm, ChangeSelfForm
from app.constants import Access
from app.utils import get_mentor, admin_required


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/list', methods=['GET', 'POST'])
@admin_required
def index():
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
        flash('%s %s добавлен' % (new_mentor.access, new_mentor.username))
        return redirect(url_for('admins.index', page=page))

    data = Mentor.query.filter(
        # Администраторов может добавлять только главный администратор
        Mentor.access_level < current_user.access_level
    ).order_by(
        Mentor.access_level.desc(), Mentor.last_name, Mentor.first_name, Mentor.username
    ).paginate(
        page, app.config['MENTORS_PER_PAGE'], False
    )
    g.url_for = 'admins.index'

    return render_template('data_list.html', form=form,
                           data=data, title='Список менторов')


@bp.route('/self', methods=['GET', 'POST'])
def self_mentor():
    return redirect(url_for('admins.mentor', username=current_user.username))


@bp.route('/user/<username>', methods=['GET', 'POST'])
def mentor(username):
    if username != current_user.username and \
            current_user.access_level not in [Access.ADMIN, Access.SUPER_ADMIN]:
        return redirect(url_for('main.index'))

    user = get_mentor(username)

    if user.id == current_user.id:
        form = ChangeSelfForm(user=user)
    else:
        form = ChangeMentorForm(current_access=current_user.access_level,
                                user=user)

    group_form = None
    if user.access_level == Access.MENTOR:
        group_form = GroupMentorForm(user)

    request_form = request.form

    if not request_form.get('submit', None):
        return render_template('admins/mentor_page.html', group_form=group_form,
                               form=form, mentor=user, title=user.username)

    if request_form['submit'] == 'Изменить' and form.validate_on_submit():
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data

        if form.password.data:
            user.set_password(form.password.data)

        if type(form) != ChangeSelfForm and \
                form.access_levels.data < current_user.access_level and \
                user.id != current_user.id:
            user.access_level = form.access_levels.data

            if form.access_levels.data in [Access.MENTOR, Access.UP_MENTOR] and \
                    user.id != current_user.id:
                user.discipline_id = form.disciplines.data

        db.session.commit()
        flash('%s %s Изменен' % (user.access, user.username))
        return redirect(url_for('admins.mentor', username=user.username))

    if request_form['submit'] == 'Добавить' and group_form.validate_on_submit():
        current_group = Group.query.filter_by(id=group_form.groups.data).first()
        user.add_group(current_group)
        db.session.commit()

        flash("Группа %s добавлена наставнику %s" % (current_group.name, user.username))

        return redirect(url_for('admins.mentor', username=user.username))

    return render_template('admins/mentor_page.html', group_form=group_form,
                           form=form, mentor=user, title=user.username)


@bp.route('/remove/<username>')
@admin_required
def remove_mentor(username):
    user = get_mentor(username)

    if user.id != current_user.id:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('admins.index'))
