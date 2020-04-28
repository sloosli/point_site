from flask import render_template, flash, redirect, url_for, g, request
from flask_login import current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import (Student, Group, Theme, DisciplinePointRecord, ReferPointRecord,
                        OrderRecord, Order)
from app.main import bp
from app.main.forms import (GroupForm, ChangeGroupForm, DisciplineRecordForm,
                            ReferRecordForm, OrderRecordForm, OrderForm)
from app.constants import Access, navs, OrderStatus
from app.utils import (admin_required, angel_required, get_group, get_student, is_admin,
                       get_discipline_records, get_vk_users_data)


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
    return redirect(url_for('students.list'))


@bp.route('/order/list', methods=['GET', 'POST'])
@angel_required
def order_list():
    page = request.args.get('page', 1, type=int)

    orders = Order.query.order_by(
        Order.name
    )
    orders = orders.paginate(
        page, app.config['GROUPS_PER_PAGE'], False
    )
    if current_user.access_level == Access.ANGEL:
        return render_template('data_list.html',
                               title='Список подарков', data=orders)

    form = OrderForm()
    if form.validate_on_submit():
        order = Order(name=form.name.data,
                      cost=form.cost.data,
                      description=form.description.data,
                      type_id=form.type.data)
        db.session.add(order)
        db.session.commit()

        flash("Подарок %s добавлен" % order.name)

        return redirect(url_for('main.order_list'))

    return render_template('data_list.html', form=form,
                           title='Список подарков', data=orders)


@bp.route('/order/id/<order_id>', methods=['GET', 'POST'])
@angel_required
def order(order_id):
    current_order = Order.query.get(order_id)

    return render_template('main/order_page.html', order=current_order)


@bp.route('/order/remove/<order_id>')
@admin_required
def remove_order(order_id):
    order = Order.query.get(order_id)

    if order.records.count() > 0:
        flash("Удаление подарка невозможно, т.к. у него есть заказы")
        return redirect(url_for('main.order', order_id=order_id))

    db.session.delete(order)
    db.session.commit()
    flash('Подарок удален')

    return redirect(url_for('main.order_list'))


@bp.route('/group/list', methods=['GET', 'POST'])
@login_required
def group_list():
    if current_user.access_level == Access.HAWK:
        return redirect(url_for('main.student_list'))

    page = request.args.get('page', 1, type=int)
    form = None
    if is_admin(current_user):
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


@bp.route('/group/id/<group_id>', methods=['GET', 'POST'])
@login_required
def group(group_id):
    current_group = get_group(group_id)
    if current_user.access_level in [Access.MENTOR, Access.UP_MENTOR] and \
            current_user.discipline_id != current_group.discipline_id:
        return redirect(url_for('main.index'))

    form = None
    if is_admin(current_user):
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


@bp.route('/group/id/<group_id>/add_multiple', methods=['POST'])
@login_required
def group_add_students(group_id):
    r_form = request.form

    users = get_vk_users_data(r_form)
    students = []
    for user in users:
        student = Student.query.filter_by(vk_id=user['id']).first()
        if student is None:
            student = Student(first_name=user['first_name'],
                              last_name=user['last_name'],
                              vk_id=user['id'])
            db.session.add(student)
            flash("Студент %s vk_id: %i Добавлен в базу" % (student.username, student.vk_id))
        students.append(student)

    group = get_group(group_id)
    for student in students:
        if student.is_in_group(group):
            flash("Студент %s vk_id: %i уже состоит в данной группе" % (student.username, student.vk_id))
        else:
            student.add_group(group)
            flash("Студент %s vk_id: %i Добавлен в группу" % (student.username, student.vk_id))

    db.session.commit()
    return redirect(url_for('main.group', group_id=group_id))


@bp.route('/group/id/<group_id>/remove/<student_id>')
@login_required
def remove_user(group_id, student_id):
    group = get_group(group_id)
    student = get_student(student_id)
    student.remove_group(group)
    db.session.commit()
    return redirect(url_for('main.group', group_id=group_id))


@bp.route('/table/discipline/<student_id>', methods=['GET', 'POST'])
@login_required
def disc_table(student_id):
    current_student = get_student(student_id)

    if current_user.access_level == Access.MENTOR:
        m_gr = set(current_user.groups)
        s_gr = set(current_student.groups)
        if not m_gr & s_gr:
            flash("У вас недостаточно прав для просмота данной страницы")
            return redirect(url_for('main.index'))

    if current_user.access_level == Access.HAWK:
        flash("У вас недостаточно прав для просмота данной страницы")
        return redirect(url_for('main.index'))

    student_disc = current_student.groups.with_entities(Group.discipline_id)
    busy_theme = current_student.discipline_records.with_entities(
        DisciplinePointRecord.theme_id
    )
    vacant_theme = Theme.query.filter(
        Theme.id.notin_(busy_theme)).filter(
        Theme.discipline_id.in_(student_disc)
    )

    if current_user.access_level in [Access.MENTOR, Access.UP_MENTOR]:
        vacant_theme = vacant_theme.filter_by(discipline=current_user.discipline)

    vacant_theme = vacant_theme.order_by(
        Theme.name
    )

    form = DisciplineRecordForm(vacant_theme)
    records = get_discipline_records(current_student).all()
    records = sorted(records, key=lambda x: (x.theme.discipline.name, x.theme.name))

    if form.validate_on_submit():
        theme = Theme.query.get(form.themes.data)
        new_rec = DisciplinePointRecord(theme_id=form.themes.data,
                                        mentor_id=current_user.id,
                                        student_id=current_student.id)
        new_rec.amount = theme.max_points
        db.session.add(new_rec)
        db.session.commit()

        flash("Запись добавлена")
        return redirect(url_for('main.disc_table', student_id=student_id))

    return render_template('main/table.html', form=form,
                           student=current_student, title="Баллы за учебу",
                           records=records, type=DisciplinePointRecord,
                           back=[url_for('students.student', student_id=student_id),
                                 current_student.username])


@bp.route('/table/referal/<student_id>', methods=['GET', 'POST'])
@login_required
def refer_table(student_id):
    current_student = get_student(student_id)

    if current_user.access_level < Access.HAWK:
        flash("У вас недостаточно прав для просмота данной страницы")
        return redirect(url_for('main.index'))

    form = ReferRecordForm()
    records = current_student.refer_records
    records = sorted(records, key=lambda x: x.timestamp)

    if form.validate_on_submit():
        new_rec = ReferPointRecord(refer_vk_id=form.referal.data,
                                   amount=app.config['REFER_RECORD_POINTS'],
                                   student_id=current_student.id,
                                   mentor_id=current_user.id)

        db.session.add(new_rec)
        db.session.commit()
        flash("Запись добавлена")
        return redirect(url_for('main.refer_table', student_id=student_id))

    return render_template('main/table.html', form=form,
                           student=current_student, title="Баллы за приглашения",
                           records=records, type=ReferPointRecord,
                           back=[url_for('students.student', student_id=student_id),
                                 current_student.username])


@bp.route('/table/orders/<student_id>', methods=['GET', 'POST'])
@login_required
def order_table(student_id):
    current_student = get_student(student_id)

    if current_user.access_level < Access.ANGEL:
        flash("У вас недостаточно прав для просмота данной страницы")
        return redirect(url_for('main.index'))

    form = OrderRecordForm(student=current_student)
    records = current_student.order_records
    records = sorted(records, key=lambda x: x.timestamp)

    if form.validate_on_submit():
        order = Order.query.get(form.orders.data)
        if current_student.total_points() < order.cost:
            flash("У данного студента недостаточно баллов")
        else:
            new_rec = OrderRecord(cost=order.cost,
                                  status_id=OrderStatus.Ordered,
                                  commentary=form.commentary.data,
                                  student_id=current_student.id,
                                  order_id=order.id)

            db.session.add(new_rec)
            db.session.commit()

        return redirect(url_for('main.order_table', student_id=student_id))

    return render_template('main/table.html', form=form,
                           student=current_student, title="Заказы",
                           records=records, type=OrderRecord,
                           back=[url_for('students.student', student_id=student_id),
                                 current_student.username])


@bp.route('/table/orders/by_set/done/<order_id>')
@login_required
def done_order_by_set(order_id):
    if current_user.access_level < Access.ANGEL:
        flash("У вас недостаточно прав для просмота данной страницы")
        return redirect(url_for('main.index'))

    order = Order.query.get(order_id)

    page = request.args.get('page', 1, type=int)
    records = OrderRecord.query.filter_by(order_id=order_id, status_id=OrderStatus.Done)
    records = records.paginate(
        page, app.config['RECORDS_PER_PAGE'], False
    )

    return render_template('main/table.html', title=order.name,
                           records=records.items, type=OrderRecord,
                           page=records.page, pages=records.pages)


@bp.route('/table/orders/by_set/ordered/<order_id>')
@login_required
def ordered_order_by_set(order_id):
    if current_user.access_level < Access.ANGEL:
        flash("У вас недостаточно прав для просмота данной страницы")
        return redirect(url_for('main.index'))

    order = Order.query.get(order_id)

    page = request.args.get('page', 1, type=int)
    records = OrderRecord.query.filter_by(order_id=order_id, status_id=OrderStatus.Ordered)
    records = records.paginate(
        page, app.config['RECORDS_PER_PAGE'], False
    )

    return render_template('main/table.html', title=order.name,
                           records=records.items, type=OrderRecord,
                           page=records.page, pages=records.pages)


@bp.route('/order_record/set_done/<record_id>')
@angel_required
def set_order_done(record_id):
    record = OrderRecord.query.get(record_id)
    if record.status_id == 3:
        return "not ok", 500
    student_id = record.student_id
    record.status_id = OrderStatus.Done
    db.session.commit()

    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('students.student', student_id=student_id)
    return redirect(next_page)


@bp.route('/order_record/delete/<record_id>')
@admin_required
def delete_order_record(record_id):
    record = OrderRecord.query.get(record_id)
    student_id = record.student_id

    db.session.delete(record)
    db.session.commit()

    flash("Заказ успешно удален")
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('students.student', student_id=student_id)
    return redirect(next_page)


@bp.route('/discipline_record/delete/<record_id>')
@admin_required
def delete_discipline_record(record_id):
    record = DisciplinePointRecord.query.get(record_id)
    student_id = record.student_id

    db.session.delete(record)
    db.session.commit()

    flash("Запись успешно удалена")
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('main.disc_table', student_id=student_id)
    return redirect(next_page)


@bp.route('/refer_record/delete/<record_id>')
@admin_required
def delete_refer_record(record_id):
    record = ReferPointRecord.query.get(record_id)
    student_id = record.student_id

    db.session.delete(record)
    db.session.commit()

    flash("Запись успешно удалена")
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('main.refer_table', student_id=student_id)
    return redirect(next_page)
