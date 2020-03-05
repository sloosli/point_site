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

    group = VkGroup.get(data['group_id'])
    if 'secret' not in data or data['secret'] != group.secret_key:
        return 'not ok'

    if data['type'] == 'confirmation':
        return group.confirmation_key

    vk_session = vk_api.VkApi(token=group.token)
    vk = vk_session.get_api()

    if data['type'] == 'message_new':
        from_id = data['object']['from_id']
        student = Student.get(int(from_id))
        vk.messages.send(
            message=group.asnwer(student),
            random_id=get_random_id(),
            perr_id=from_id
        )

    return 'ok'
