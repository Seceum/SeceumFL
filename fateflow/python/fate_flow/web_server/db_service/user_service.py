# import peewee
# from werkzeug.security import generate_password_hash, check_password_hash
#
# from fate_flow.db.db_models import DB
# from fate_flow.web_server.db.db_models import User, StudioSysRole, StudioSysFunction
# from fate_flow.web_server.db_service.common_service import CommonService
# from fate_flow.web_server.utils.common_util import get_uuid
# from fate_flow.web_server.utils.enums import StatusEnum
#
#
# class UserService(CommonService):
#     model = User
#
#     @classmethod
#     @DB.connection_context()
#     def filter_by_id(cls, user_id):
#         try:
#             user = cls.model.select().where(cls.model.id == user_id).get()
#             return user
#         except peewee.DoesNotExist:
#             return None
#
#     @classmethod
#     @DB.connection_context()
#     def query_user(cls, username, password):
#         user = cls.model.select().where((User.username == username), (User.status == StatusEnum.VALID.value)).first()
#         # if user and user.check_password(password):
#         if user and check_password_hash(str(user.password), password):
#             return user
#         else:
#             return None
#
#     @classmethod
#     @DB.connection_context()
#     def save(cls, **kwargs):
#         if "id" not in kwargs:
#             kwargs["id"] = get_uuid()
#         if "alternative_id" not in kwargs:
#             kwargs["alternative_id"] = get_uuid()
#         kwargs["password"] = generate_password_hash(str(kwargs["password"]))
#         sample_obj = cls.model(**kwargs).save(force_insert=True)
#         return sample_obj
#
#     @classmethod
#     @DB.connection_context()
#     def query_username(cls, username, user_id):
#         return cls.model.select().where(cls.model.username == username, cls.model.id != user_id)
#
#
# class RoleService(CommonService):
#     model = StudioSysRole
#
#     @classmethod
#     @DB.connection_context()
#     def get_roles(cls, role_codes, status=StatusEnum.VALID.value):
#         roles = cls.model.select().where(cls.model.code.in_(role_codes), cls.model.status == status)
#         return roles
#
#
# class SysFunctionService(CommonService):
#     model = StudioSysFunction
#
#     @classmethod
#     @DB.connection_context()
#     def query_by_codes(cls, codes, status=StatusEnum.VALID.value):
#         roles = cls.model.select().where(cls.model.code.in_(codes), cls.model.status == status)
#         return roles