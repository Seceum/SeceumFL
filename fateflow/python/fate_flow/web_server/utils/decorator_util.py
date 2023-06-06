from functools import wraps
from flask_login import current_user
from flask_socketio import disconnect


def authenticated_only(func):
    @wraps(func)
    def wraped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return func(*args, **kwargs)
        return wraped
