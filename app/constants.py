from flask import url_for


class Access:
    MENTOR = 1
    UP_MENTOR = 2
    HAWK = 3
    ANGEL = 4
    ADMIN = 5
    SUPER_ADMIN = 6


class Nav:
    def __init__(self, *args):
        self.name = args[0]
        self.url = args[1]


students = Nav('Студенты', 'main.student_list')
groups = Nav('Группы', 'main.group_list')
mentors = Nav('Менторы', 'admins.mentor_list')
my_profile = Nav('Мой профиль', 'admins.self_mentor')
disciplines = Nav('Предметы', 'admins.discipline_list')

navs = {
    Access.MENTOR: [groups],
    Access.UP_MENTOR: [groups],
    Access.HAWK: [students],
    Access.ANGEL: [groups, students],
    Access.ADMIN: [groups, students, mentors, disciplines, my_profile],
    Access.SUPER_ADMIN: [groups, students, mentors, disciplines, my_profile],
}
