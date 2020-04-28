

# Доступ
class Access:
    MENTOR = 1
    UP_MENTOR = 2
    HAWK = 3
    ANGEL = 4
    ADMIN = 5
    SUPER_ADMIN = 6


access_desc = {
    Access.MENTOR: 'Наставник',
    Access.UP_MENTOR: 'Главный наставник',
    Access.HAWK: 'Ястреб',
    Access.ANGEL: 'Ангел',
    Access.ADMIN: 'Администратор',
    Access.SUPER_ADMIN: 'Главный администратор',
}


# Навигация
class Nav:
    def __init__(self, *args):
        self.name = args[0]
        self.url = args[1]


students = Nav('Студенты', 'students.list')
groups = Nav('Группы', 'main.group_list')
mentors = Nav('Менторы', 'admins.index')
disciplines = Nav('Предметы', 'disciplines.index')
orders = Nav('Подарки', 'main.order_list')
communities = Nav('Сообщества', 'communities.list')

navs = {
    Access.MENTOR: [groups],
    Access.UP_MENTOR: [groups, mentors],
    Access.HAWK: [students],
    Access.ANGEL: [groups, students, orders],
    Access.ADMIN: [groups, students, disciplines, orders, mentors, communities],
    Access.SUPER_ADMIN: [groups, students, disciplines, orders, mentors, communities]
}

# Сообщества
default_message = "Привет, {username}. У тебя {points} баллов"


# Заказы
class Orders:
    Set = 1
    Discount = 2

    _desc = [["Не отправлен", "Отправлен", "Получен"],
             ["Не отправлена", "Отправлена", "Использована"]]

    @classmethod
    def status(cls, type_id, status_id):
        return cls._desc[type_id - 1][status_id - 1]


class OrderStatus:
    Ordered = 1
    Sent = 2
    Done = 3
