
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
my_profile = Nav('Мой профиль', 'admins.self_mentor')
disciplines = Nav('Предметы', 'disciplines.index')

navs = {
    Access.MENTOR: [groups],
    Access.UP_MENTOR: [groups],
    Access.HAWK: [students],
    Access.ANGEL: [groups, students],
    Access.ADMIN: [groups, students, mentors, disciplines, my_profile],
    Access.SUPER_ADMIN: [groups, students, mentors, disciplines, my_profile],
}

# Сообщества

default_message = "Привет, "

