from flask import request
import vk_api
from vk_api.utils import get_random_id
from app.models import VkGroup, Student
from app.communities import bp


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
                message=group.asnwer(student),
                random_id=get_random_id(),
                peer_id=from_id
            )

    return 'ok'
