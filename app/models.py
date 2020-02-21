from datetime import datetime
from flask import get_template_attribute
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login

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

    access_level = db.Column(db.Integer, db.ForeignKey('access_level.id'))
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'))

    discipline_records = db.relationship('DisciplinePointRecord', backref='mentor', lazy='dynamic')
    refer_records = db.relationship('ReferPointRecord', backref='mentor', lazy='dynamic')
    groups = db.relationship('Group',
                             secondary=group_mentors,
                             backref='mentors',
                             lazy='dynamic')

    def __repr__(self):
        return '<User> %s' % self.username

    def to_html(self):
        render = get_template_attribute('admins/_mentor.html', 'render')
        return render(self)

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


class AccessLevel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)

    mentors = db.relationship('Mentor', backref='access', lazy='dynamic')


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    vk_id = db.Column(db.Integer, unique=True)

    discipline_records = db.relationship('DisciplinePointRecord', backref='student', lazy='dynamic')
    refer_records = db.relationship('ReferPointRecord', backref='student', lazy='dynamic')
    groups = db.relationship('Group',
                             secondary=group_students,
                             backref='students',
                             lazy='dynamic')

    @property
    def username(self):
        return self.last_name + ' ' + self.first_name

    def to_html(self):
        render = get_template_attribute('main/_student.html', 'render')
        return render(self)

    def total_points(self):
        if self.discipline_records or self.refer_records:
            return sum(map(lambda x: x.amount, self.discipline_records)) + \
                   sum(map(lambda x: x.amount, self.refer_records))
        return 0

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
    name = db.Column(db.String(32))

    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'))


class Discipline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))

    groups = db.relationship('Group', backref='discipline', lazy='dynamic')
    mentors = db.relationship('Mentor', backref='discipline', lazy='dynamic')


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


class ReferPointRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refer_vk_id = db.Column(db.Integer, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    amount = db.Column(db.Integer)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.id'))


class VkGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    confirmation_key = db.Column(db.String(32))
    secret_key = db.Column(db.String(64))
