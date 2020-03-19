import secrets
from flask import request, redirect, url_for, render_template, flash, g
import vk_api
from vk_api.utils import get_random_id
from app import app, db
from app.models import VkGroup, Student
from app.communities import bp
from app.communities.forms import VkGroupform
from app.utils import admin_required


# Адрес для запроса боту
@bp.route('/bot', methods=['POST'])
def bot():
    data = request.get_json()
    if not data or \
            'type' not in data or 'group_id' not in data:
        return 'not ok'

    group = VkGroup.query.get(data['group_id'])
    if group is None or \
            'secret' not in data or \
            data['secret'] != group.secret_key:
        return 'not ok'

    if data['type'] == 'confirmation':
        return group.confirmation_key

    vk_session = vk_api.VkApi(token=group.token)
    vk = vk_session.get_api()

    if data['type'] == 'message_new':
        from_id = data['object']['message']['from_id']
        student = Student.query.filter_by(vk_id=from_id).first()
        if student is None:
            vk.messages.send(
                message='Ты не являешься нашим учеником(',
                random_id=get_random_id(),
                peer_id=from_id
            )

        else:
            vk.messages.send(
                message=group.answer(student),
                random_id=get_random_id(),
                peer_id=from_id
            )

    return 'ok'


@bp.route('/list', methods=['GET', 'POST'])
@admin_required
def list():
    data = VkGroup.query.order_by(VkGroup.name)

    form = VkGroupform()
    page = request.args.get('page', 1, type=int)

    if form.validate_on_submit():
        vk_session = vk_api.VkApi()
        vk = vk_session.get_api()

        id = form.vk_id.data
        token = form.token.data
        confirm = vk.groups.getCallbackConfirmationCode(group_id=id)
        name = vk.groups.getById(group_id=id)[0]['name']
        secret_key = secrets.token_hex(32)

        group = VkGroup(id=id, name=name, token=token,
                        confirmation_key=confirm, secret_key=secret_key)
        db.session.add(group)
        db.session.commit()

        vk.groups.addCallbackServer(group_id=id, title="Point Site", secret_key=secret_key,
                                    url=app.config['BOT_URL'])

        flash('Группа %s добавлена' % group.name)
        return redirect(url_for('admins.index', page=page))

    data = VkGroup.query.order_by(VkGroup.name).paginate(
        page, 20, False
    )
    g.url_for = 'communities.list'

    return render_template('data_list.html', form=form,
                           data=data, title='Список сообществ')
