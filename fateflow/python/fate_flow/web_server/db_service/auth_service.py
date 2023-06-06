import peewee
from werkzeug.security import generate_password_hash, check_password_hash

from fate_flow.db.db_models import DB
from fate_flow.web_server.db.db_models import StudioAuthUser, StudioAuthRole, StudioAuthPermission, StudioAuthGroup, \
    StudioUserGroup, StudioUserRole, StudioRolePermission, StudioUserPermission
from fate_flow.web_server.db_service.common_service import CommonService
from fate_flow.web_server.utils.common_util import get_uuid, get_format_time
from fate_flow.web_server.utils.enums import StatusEnum


class UserService(CommonService):
    model = StudioAuthUser

    @classmethod
    @DB.connection_context()
    def filter_by_id(cls, user_id):
        try:
            user = cls.model.select().where(cls.model.id == user_id).get()
            return user
        except peewee.DoesNotExist:
            return None

    @classmethod
    @DB.connection_context()
    def query_user(cls, username, password):
        user = cls.model.select().where((cls.model.username == username),
                                        (cls.model.status == StatusEnum.VALID.value)).first()
        if user and check_password_hash(str(user.password), password):
            return user
        else:
            return None

    @classmethod
    @DB.connection_context()
    def save(cls, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
        if "alternative_id" not in kwargs:
            kwargs["alternative_id"] = get_uuid()
        kwargs["password"] = generate_password_hash(str(kwargs["password"]))
        obj = cls.model(**kwargs).save(force_insert=True)
        return obj

    @classmethod
    @DB.connection_context()
    def query_username(cls, username, user_id):
        return cls.model.select().where(cls.model.username == username, cls.model.id != user_id)

    @classmethod
    @DB.connection_context()
    def query_by_team(cls, team_id):
        if team_id:
            user_objs = cls.model.select(cls.model.id.alias("user_id"), cls.model.username, cls.model.nickname,
                                         cls.model.create_time).join(StudioUserGroup, on=(
                    cls.model.id == StudioUserGroup.user_id)).where(StudioUserGroup.group_id == team_id,
                                                                    cls.model.status == StatusEnum.VALID.value).distinct()
        else:
            user_objs = cls.model.select(cls.model.id.alias("user_id"), cls.model.username, cls.model.nickname,
                                         cls.model.create_time).where(
                cls.model.status == StatusEnum.VALID.value,cls.model.is_superuser == 0)
        return user_objs

    @classmethod
    @DB.connection_context()
    def create_user(cls, user_dict, team_user_list, role_user_list, user_permission_list):
        with DB.atomic():
            cls.model(**user_dict).save(force_insert=True)
            for team_user_dict in team_user_list:
                StudioUserGroup(**team_user_dict).save(force_insert=True)
            for role_user_dict in role_user_list:
                StudioUserRole(**role_user_dict).save(force_insert=True)
            if user_permission_list:
                StudioUserPermission.insert_many(user_permission_list).execute()

    @classmethod
    @DB.connection_context()
    def delete_user(cls, user_ids, update_user_dict):
        with DB.atomic():
            cls.model.update(update_user_dict).where(cls.model.id.in_(user_ids)).execute()
            StudioUserGroup.delete().where(StudioUserGroup.user_id.in_(user_ids)).execute()
            StudioUserRole.delete().where(StudioUserRole.user_id.in_(user_ids)).execute()
            StudioUserPermission.delete().where(StudioUserPermission.user_id.in_(user_ids)).execute()

    @classmethod
    @DB.connection_context()
    def update_user(cls, user_id, user_dict, team_list, target_role_id_list, permission_codes, user_name):
        date_time = get_format_time()
        permission_list = []
        for permission_code in permission_codes:
            permission_list.append({
                "id": get_uuid(),
                "user_id": user_id,
                "permission_code": permission_code,
                "creator": user_name,
                "create_time": get_format_time()
            })
        with DB.atomic():
            if user_dict:
                user_dict["update_time"] = date_time
                user_dict["updator"] = user_name
                cls.model.update(user_dict).where(cls.model.id == user_id).execute()
            if team_list:
                user_group_obj = StudioUserGroup.query(user_id=user_id).first()
                StudioUserGroup.delete().where(StudioUserGroup.user_id == user_id).execute()
                if user_group_obj:
                    target_team_id_list=[{"id": get_uuid(),
                             "group_id": group_id,
                             "user_id": user_id,
                             "creator": user_group_obj.creator,
                             "create_time": user_group_obj.create_time,
                             "updator": user_name,
                             "update_time": date_time} for group_id in team_list]
                else:
                    target_team_id_list=[{"id": get_uuid(),
                             "group_id": group_id,
                             "user_id": user_id,
                             "updator": user_name,
                             "update_time": date_time} for group_id in team_list]
                StudioUserGroup.insert_many(target_team_id_list).execute()
            if target_role_id_list:
                role_obj = StudioUserRole.query(user_id=user_id).first()
                StudioUserRole.delete().where(StudioUserRole.user_id == user_id).execute()
                if role_obj:
                    role_id_list = [{"id": get_uuid(), "role_id": role_id, "updator": user_name,"user_id": user_id,
                                       "update_time": date_time, "creator": role_obj.creator,
                                       "create_time": role_obj.create_time} for role_id in target_role_id_list]
                else:
                    role_id_list = [{"id": get_uuid(), "role_id": role_id, "updator": user_name,"user_id": user_id,
                                       "update_time": date_time,
                                       } for role_id in target_role_id_list]
                StudioUserRole.insert_many(role_id_list).execute()
            StudioUserPermission.delete().where(StudioUserPermission.user_id == user_id).execute()
            if permission_list:
                StudioUserPermission.insert_many(permission_list).execute()


class RoleService(CommonService):
    model = StudioAuthRole

    @classmethod
    @DB.connection_context()
    def query_by_user_list(cls, user_ids):
        in_filters_tuple_list = cls.cut_list(user_ids, 20)
        res_list = []
        for i in in_filters_tuple_list:
            user_objs = cls.model.select(cls.model.id.alias("role_id"), cls.model.name.alias("role_name"),
                                         StudioUserRole.user_id).join(
                StudioUserRole, on=(
                        cls.model.id == StudioUserRole.role_id)).where(StudioUserRole.user_id.in_(i))
            if user_objs:
                res_list.extend(list(user_objs.dicts()))
        return res_list

    @classmethod
    @DB.connection_context()
    def create_by_permission(cls, role_dict, permission_codes, user_name):
        permission_list = []
        with DB.atomic():
            cls.model(**role_dict).save(force_insert=True)
            for permission_code in permission_codes:
                permission_list.append({
                    "id": get_uuid(),
                    "role_id": role_dict["id"],
                    "permission_code": permission_code,
                    "creator": user_name,
                    "create_time": get_format_time()
                })
            if permission_list:
                StudioRolePermission.insert_many(permission_list).execute()


class PermissionService(CommonService):
    model = StudioAuthPermission

    @classmethod
    @DB.connection_context()
    def query_by_codes(cls, codes, status=StatusEnum.VALID.value):
        roles = cls.model.select().where(cls.model.code.in_(codes), cls.model.status == status)
        return roles


class GroupService(CommonService):
    model = StudioAuthGroup

    @classmethod
    @DB.connection_context()
    def total_delete(cls, team_id, user_ids, user_update_dict):
        in_filters_tuple_list = cls.cut_list(user_ids, 20)
        with DB.atomic():
            cls.model.delete().where(cls.model.id == team_id).execute()
            StudioUserGroup.delete().where(StudioUserGroup.group_id == team_id).execute()
            # for user_id in in_filters_tuple_list:
                # StudioUserRole.delete().where(StudioUserRole.user_id.in_(user_id))
                # StudioAuthUser.update(user_update_dict).where(StudioAuthUser.id.in_(user_id)).execute()

    @classmethod
    @DB.connection_context()
    def get_by_user_id(cls, user_id, cols):
        group_objs = cls.model.select(*cols).join(StudioUserGroup, join_type=peewee.JOIN.LEFT_OUTER,
                                                  on=(cls.model.id == StudioUserGroup.group_id)).where(
            StudioUserGroup.user_id == user_id)

        return group_objs


class UserGroupService(CommonService):
    model = StudioUserGroup

    @classmethod
    @DB.connection_context()
    def user_move(cls, target_team_id, origin_team_id, user_ids, user_name):
        with DB.atomic():
            cls.model.delete().where(UserGroupService.model.user_id.in_(user_ids),
                                     UserGroupService.model.group_id.in_([target_team_id, origin_team_id])).execute()
            user_group_list = []
            create_time = get_format_time()
            for user_id in user_ids:
                user_group_list.append({
                    "id": get_uuid(),
                    "group_id": target_team_id,
                    "user_id": user_id,
                    "creator": user_name,
                    "create_time": create_time
                })
            cls.model.insert_many(user_group_list).execute()

    @classmethod
    @DB.connection_context()
    def user_delete(cls, origin_team_id, user_ids):
        with DB.atomic():
            cls.model.delete().where(UserGroupService.model.user_id.in_(user_ids),
                                     UserGroupService.model.group_id.in_([ origin_team_id])).execute()


class UserRoleService(CommonService):
    model = StudioUserRole


class UserPermissionService(CommonService):
    model = StudioUserPermission


class RolePermissionService(CommonService):
    model = StudioRolePermission

    @classmethod
    @DB.connection_context()
    def permission_list(cls, role_id=None):
        role_objs = cls.model.select(StudioAuthRole.id.alias("role_id"), StudioAuthRole.name, StudioAuthRole.comments,
                                     cls.model.permission_code, StudioAuthRole.create_time).join(
            StudioAuthRole, on=(cls.model.role_id == StudioAuthRole.id))
        if role_id:
            res_objs = role_objs.where(cls.model.role_id.in_(role_id)).order_by(StudioAuthRole.create_time.desc()).distinct()
        else:
            res_objs = []
            # res_objs = role_objs.order_by(StudioAuthRole.create_time.desc())
        return res_objs

    @classmethod
    @DB.connection_context()
    def update_by_permission(cls, role_id, permission_codes, user_name):
        permission_list = []
        with DB.atomic():
            cls.model.delete().where(cls.model.role_id == role_id).execute()
            for permission_code in permission_codes:
                permission_list.append({
                    "id": get_uuid(),
                    "role_id": role_id,
                    "permission_code": permission_code,
                    "creator": user_name,
                    "create_time": get_format_time()
                })
            if permission_list:
                StudioRolePermission.insert_many(permission_list).execute()
