import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Loakdf9(a-03m34nmf0'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GROUPS_PER_PAGE = 4
    MENTORS_PER_PAGE = 12
    STUDENTS_PER_PAGE = 12
    RECORDS_PER_PAGE = 20

    BOT_URL = "bonus-point-site.herokuapp.com/communities/bot"

    VK_SERVICE_KEY = '436dda3f436dda3f436dda3f9c431dc2a74436d436dda3f1d0d98e3aee65cafefd50e11'
