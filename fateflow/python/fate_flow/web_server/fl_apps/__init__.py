from datetime import timedelta

import itsdangerous
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_cors import CORS
from fate_flow.apps import app
from fate_flow.db.db_models import DB
from fate_flow.settings import stat_logger
from fate_flow.web_server.db_service.auth_service import UserService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.enums import StatusEnum

app.secret_key = config.secret_key
CORS(app, supports_credentials=True,max_age = 2592000)
# socketio = SocketIO(app, async_mode=None, cors_allowed_origins='*')
login_manager = LoginManager()
login_manager.init_app(app)


# app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
# login_manager.remember_cookie_duration = timedelta(days=2)

@app.teardown_request
def _db_close(exc):
    if not DB.is_closed():
        DB.close()


# @login_manager.user_loader
# def load_user(user_id):
#     return UserService.filter_by_id(user_id)

@login_manager.request_loader
def load_user(web_request):
    jwt = itsdangerous.TimedJSONWebSignatureSerializer(secret_key=config.secret_key, expires_in=config.token_expires_in)
    authorization = web_request.headers.get("Authorization")
    if authorization:
        try:
            alternative_id = str(jwt.loads(authorization))
            user = UserService.query(alternative_id=alternative_id, status=StatusEnum.VALID.value)
            if user:
                return user[0]
            else:
                return None
        except Exception as e:
            stat_logger.exception(e)
            return None
    else:
        return None
