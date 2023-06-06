from threading import Lock

import itsdangerous
from flask import render_template, request, Flask
from flask_login import current_user, login_user
from flask_socketio import SocketIO, emit

from fate_flow.web_server.db.db_models import StudioAuthUser
from fate_flow.web_server.db_service.auth_service import UserService
from fate_flow.web_server.db_service.model_service import ModelInfoExtendService
from fate_flow.web_server.db_service.sample_service import SampleAuthorizeService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.enums import RoleTypeEnum, StatusEnum
from fate_flow.web_server.utils.websocket_util import GetLogInfo, get_run_ips
import requests
from fate_arch.common.conf_utils import get_base_config
async_mode = None
app = Flask(__name__)
app.secret_key = config.secret_key
# CORS(app, supports_credentials=True)
socketio = SocketIO(app, async_mode=None, cors_allowed_origins='*')
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app, async_mode=async_mode,cors_allowed_origins='*')
thread = None
thread_lock = Lock()
sessions ={}
role = RoleTypeEnum.GUEST.value
party_id = config.local_party_id
def auth_required(authorization):
    jwt = itsdangerous.TimedJSONWebSignatureSerializer(secret_key=config.secret_key, expires_in=config.token_expires_in)
    if authorization:
        try:
            alternative_id = str(jwt.loads(authorization))
            user = UserService.query(alternative_id=alternative_id, status=StatusEnum.VALID.value).first()
            # login_user(user)
            if user:
                return user
            else:
                return False
        except Exception as e:
            return False
    else:
        return False
def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(3)
        # print("房间长度",len(sessions))
        try:
            for session_id,obj in sessions.items():
                # permissions = obj[].get_permission_code(obj["current_user"])
                data_auth_num = 0
                model_auth_num = 0
                if "080101" in obj["permissions"]:
                    data_auth_num =  SampleAuthorizeService.count_no_approve()
                if "030302" in obj["permissions"]:
                    model_auth_num = ModelInfoExtendService.count_no_approve()
                data = {
                    "data_auth_num": data_auth_num,
                    "model_auth_num":model_auth_num ,
                }
                socketio.emit('data_count',
                              {'data': data}, to=session_id)
                if obj["job_id"]:
                    job_run_ips = get_run_ips(obj["job_id"], role, party_id)
                    data = GetLogInfo(job_run_ips, obj["job_id"], role, party_id).get_log_size()
                    # data = {"warting":10,"debug":10,"error":5,"info":5}
                    socketio.emit('log_count',
                                  {'data': data}, to=session_id)
        except Exception as e:
            print(e)
            pass



@app.route('/v1/socket', methods=['post', 'get'])
def socket_index():
    return render_template('index.html', async_mode=None)

@socketio.event
def join(message):
    job_id = message.get('job_id')
    if not job_id:
        emit('error_response',
             {'data': "job_id is null"},
             to=request.sid)
    else:
        sessions[request.sid]["job_id"]=job_id

@socketio.event
def leave():
    # sessions[request.sid]=""
    del sessions[request.sid]

@socketio.event
def query_log(message):
    try:
        job_id = sessions[request.sid]["job_id"]
        if job_id:
            job_run_ips = get_run_ips(job_id, role, party_id)
            data = GetLogInfo(job_run_ips, job_id, role, party_id).get_log_lines(message['type'], begin=message.get('begin'),
                                                                                 end=message.get('end'))
            emit('log_detail',
                 {'data': data},
                 to=request.sid)
        else:
            emit('error_response',
                 {'data': "job_id is null"},
                 to=request.sid)
    except:
        #会话已断开
        pass
@socketio.event
def get_token(message):
    auth = message.get("Authorization")
    # print("auth",auth)
    user = auth_required(auth)
    if not user:
        emit('error_response', {"data":"token error"})
        return
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    permissions  = user.get_permission_code()
    sessions[request.sid]={"permissions":permissions,"job_id":""}

# @socketio.event
# def connect():
#     # request.headers
#     # auth = request.headers.get("Authorization")
#     auth = request.args.get("Authorization")
#     user = auth_required(auth)
#     if not user:
#         emit('error_response', {"data":"token error"})
#         return
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = socketio.start_background_task(background_thread)
#     permissions  = user.get_permission_code()
#     sessions[request.sid]={"permissions":permissions,"job_id":""}


@socketio.on('disconnect')
def disconnect():
    try:
        del sessions[request.sid]
    except :
        pass


if __name__ == '__main__':
    port = get_base_config("web_socket_port", default=None, conf_name="fl_config.yaml")
    socketio.run(app,debug=False,host="0.0.0.0",port=port,use_reloader=False)
