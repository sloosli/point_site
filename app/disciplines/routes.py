from flask import flash, redirect, url_for, render_template, g
from app.models import Theme, Discipline
from app import db
from app.utils import admin_required
from app.disciplines import bp
from app.disciplines.forms import DisciplineForm, ThemeForm


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/list', methods=['GET', 'POST'])
@admin_required
def index():
    form = DisciplineForm()
    if form.validate_on_submit():
        # noinspection PyArgumentList
        new_discipline = Discipline(name=form.name.data)

        db.session.add(new_discipline)
        db.session.commit()
        flash('Предмет %s добавлен' % new_discipline.name)
        return redirect(url_for('disciplines.index'))

    data = Discipline.query.order_by(Discipline.name).paginate(1, 10, False)
    g.url_for = 'disciplines.index'

    return render_template('data_list.html', form=form,
                           data=data, title='Список предметов')


@bp.route('/id/<discipline_id>', methods=['GET', 'POST'])
@admin_required
def discipline(discipline_id):

    current_discipline = Discipline.query.filter_by(id=discipline_id).first_or_404()
    form = ThemeForm(current_discipline.id)

    if form.validate_on_submit():
        new_theme = Theme(name=form.name.data,
                          discipline_id=form.discipline_id,
                          max_points=form.max_points.data)
        db.session.add(new_theme)
        db.session.commit()

        flash("Тема %s добавлена" % new_theme.name)

        return redirect(url_for('disciplines.discipline', discipline_id=discipline_id))

    return render_template('disciplines/discipline_page.html', form=form,
                           discipline=current_discipline, title=current_discipline.name)


@bp.route('/remove/<discipline_id>')
@admin_required
def remove_discipline(discipline_id):
    discipline = Discipline.query.filter_by(id=discipline_id).first_or_404()

    if discipline.themes.count() > 0:
        flash('Во избежаение проблем удаление заблокировано пока у предмета существуют темы')
        return redirect(url_for('disciplines.discipline', discipline_id=discipline_id))

    db.session.delete(discipline)
    db.session.commit()

    return redirect(url_for('disciplines.index'))
