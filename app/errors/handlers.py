from flask import redirect, url_for
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return redirect(url_for('main.index'))


@bp.app_errorhandler(500)
def internal_error(error):
    return redirect(url_for('main.index'))