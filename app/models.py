from datetime import datetime
from flask import get_template_attribute, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from app.constants import Access, access_desc, default_message, Orders


group_mentors = db.Table(
    'group_mentors',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('mentor_id', db.Integer, db.ForeignKey('mentor.id'))
)

group_students = db.Table(
    'group_students',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class Mentor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    password_hash = db.Column(db.String(128))
    access_level = db.Column(db.Integer)

    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'))

    discipline_records = db.relationship('DisciplinePointRecord', backref='mentor', lazy='dynamic')
    refer_records = db.relationship('ReferPointRecord', backref='mentor', lazy='dynamic')
    groups = db.relationship('Group',
                             secondary=group_mentors,
                             backref=db.backref('mentors', lazy='dynamic'),
                             lazy='dynamic')

    @property
    def access(self):
        return access_desc[self.access_level]

    def __repr__(self):
        return '<User> %s' % self.username

    def to_html(self):
        render = get_template_attribute('admins/_mentor.html', 'render')
        return render(self)

    def is_admin(self):
        return self.access_level in [Access.ADMIN, Access.SUPER_ADMIN]

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_in_group(self, group):
        return self.groups.filter_by(id=group.id).count() > 0

    def add_group(self, group):
        if not self.is_in_group(group):
            self.groups.append(group)

    def remove_group(self, group):
        if self.is_in_group(group):
            self.groups.remove(group)


@login.user_loader
def mentor_user(id):
    return Mentor.query.get(int(id))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    vk_id = db.Column(db.Integer, unique=True)

    order_records = db.relationship('OrderRecord', backref='student', lazy='dynamic')
    discipline_records = db.relationship('DisciplinePointRecord', backref='student', lazy='dynamic')
    refer_records = db.relationship('ReferPointRecord', backref='student', lazy='dynamic')
    groups = db.relationship('Group',
                             secondary=group_students,
                             backref=db.backref('students', lazy='dynamic'),
                             lazy='dynamic')

    @property
    def username(self):
        return self.last_name + ' ' + self.first_name

    def to_html(self):
        render = get_template_attribute('main/_student.html', 'render')
        return render(self)

    def orders_cost(self):
        if self.order_records:
            return sum(map(lambda x: x.cost, self.order_records))

    def refer_points(self):
        if self.refer_records:
            return sum(map(lambda x: x.amount, self.refer_records))
        return 0

    def discipline_points(self):
        if self.discipline_records:
            return sum(map(lambda x: x.amount, self.discipline_records))
        return 0

    def total_points(self):
        return self.refer_points() + self.discipline_points() - self.orders_cost()

    def is_in_group(self, group):
        return self.groups.filter_by(id=group.id).count() > 0

    def add_group(self, group):
        if not self.is_in_group(group):
            self.groups.append(group)

    def remove_group(self, group):
        if self.is_in_group(group):
            self.groups.remove(group)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)

    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'))

    def to_html(self):
        render = get_template_attribute('main/_group.html', 'render')
        return render(self)


class Discipline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))

    groups = db.relationship('Group', backref='discipline', lazy='dynamic')
    mentors = db.relationship('Mentor', backref='discipline', lazy='dynamic')
    themes = db.relationship('Theme', backref='discipline', lazy='dynamic')

    def to_html(self):
        render = get_template_attribute('disciplines/_discipline.html', 'render')
        return render(self)


class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    max_points = db.Column(db.Integer())
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'))

    records = db.relationship('DisciplinePointRecord', backref='theme', lazy='dynamic')


class DisciplinePointRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Integer)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), index=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.id'))

    def delete_route(self):
        return url_for('main.delete_discipline_record', record_id=self.id)

    @staticmethod
    def to_header():
        render = get_template_attribute('main/_discipline_records.html', 'header')
        return render()

    def to_row(self):
        render = get_template_attribute('main/_discipline_records.html', 'render')
        return render(self)


class ReferPointRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refer_vk_id = db.Column(db.Integer, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    amount = db.Column(db.Integer)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.id'))

    def delete_route(self):
        return url_for('main.delete_refer_record', record_id=self.id)

    @staticmethod
    def to_header():
        render = get_template_attribute('main/_referal_records.html', 'header')
        return render()

    def to_row(self):
        render = get_template_attribute('main/_referal_records.html', 'render')
        return render(self)


class VkGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    token = db.Column(db.String(128))
    confirmation_key = db.Column(db.String(32))
    secret_key = db.Column(db.String(64))
    message = db.Column(db.String(256), default=default_message)

    def answer(self, student):
        message = self.message
        return message.format(username=student.username, points=student.total_points())

    def to_html(self):
        render = get_template_attribute('communities/_community.html', 'render')
        return render(self)


class OrderRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Integer)
    status_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    commentary = db.Column(db.String(256))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), index=True)

    @property
    def status(self):
        return Orders.status(self.order.type_id, self.status_id)

    def delete_route(self):
        return url_for('main.delete_order_record', record_id=self.id)

    @staticmethod
    def to_header():
        render = get_template_attribute('main/_order_records.html', 'header')
        return render()

    def to_row(self):
        render = get_template_attribute('main/_order_records.html', 'render')
        return render(self)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    cost = db.Column(db.Integer)
    description = db.Column(db.String(256))
    type_id = db.Column(db.Integer)

    records = db.relationship('OrderRecord', backref='order', lazy='dynamic')

    @property
    def type(self):
        return ['Подарок', 'Скидка'][self.type_id - 1]

    def to_html(self):
        render = get_template_attribute('main/_order.html', 'render')
        return render(self)
