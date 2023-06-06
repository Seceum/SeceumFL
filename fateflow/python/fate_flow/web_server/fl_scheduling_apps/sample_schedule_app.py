import peewee
from flask import request
from fate_flow.utils.api_utils import get_json_result
from fate_flow.web_server.db.db_models import StudioSampleAuthorize
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.db_service.sample_service import SampleService, SampleFieldsService
from fate_flow.web_server.utils.common_util import get_format_time, get_uuid
from fate_flow.web_server.utils.enums import SamplePublishStatusEnum, OwnerEnum, StatusEnum, RoleTypeEnum, SampleStatusEnum


@manager.route("/<sample_id>/<role>/<party_id>/edit_fields/<username>", methods=['POST'])
def edit_fields(sample_id,role,party_id,username):
    """自有数据_host方通知样本编辑字段"""
    sample_field_list = request.json["sample_field_list"]
    if role == RoleTypeEnum.GUEST.value:
        SampleFieldsService.update_many_by_id(sample_field_list)
    else:
        SampleFieldsService.delete_by_sample_id(sample_id)
        create_time = get_format_time()
        for sample_dict in sample_field_list:
            sample_dict["id"] = get_uuid()
            sample_dict["creator"] = username
            sample_dict["create_time"] = create_time
            sample_dict["sample_id"] = sample_id
        SampleFieldsService.insert_many(sample_field_list)
    return get_json_result(data=True)

@manager.route('/<sample_id>/<role>/<party_id>/delete_sample/<username>', methods=['POST'])
def delete_sample(sample_id, role, party_id,username):
    """自有数据_host方通知样本编辑字段"""
    SampleService.update_by_id(sample_id, {"status": SampleStatusEnum.DELETE.value,
                                                     "publish_status":SamplePublishStatusEnum.DELETE.value,
                                                     "updator": username})
    return get_json_result(data=True)

@manager.route('/<sample_id>/<role>/<party_id>/modify_publish_status/<publish_status>/<username>', methods=['POST'])
def modify_publish_status(sample_id, role, party_id,publish_status,username):
    "修改样本上下线状态"
    request_data = request.json
    party_obj=None
    if role==RoleTypeEnum.HOST.value:
        party_flag, party_obj = PartyInfoService.get_by_id(party_id)
        if not party_flag:
            return get_json_result(data=False, retmsg=f"can not find party_id {party_id}", retcode=100)
    sample_type = request_data["sample_type"]
    sample_count = request_data["sample_count"]
    sample_name = request_data["sample_name"]
    comments = request_data["comments"]
    owner = OwnerEnum.OWN.value if role ==RoleTypeEnum.GUEST.value else OwnerEnum.OTHER.value
    if publish_status == SamplePublishStatusEnum.OFF_LINE.value:
        status = SampleStatusEnum.VALID.value if role ==RoleTypeEnum.GUEST.value else SampleStatusEnum.OFF_LINE.value
        StudioSampleAuthorize.update({"approve_result": SamplePublishStatusEnum.OFF_LINE.value}).where(
            StudioSampleAuthorize.sample_id==sample_id).execute()
        SampleService.update_status(party_id, sample_id,
                                               owner, username, publish_status=publish_status,status=status)
    elif publish_status == SamplePublishStatusEnum.PUBLISHED.value:
        # 先判断外部样本中是否有数据，
        if role == RoleTypeEnum.GUEST.value:
            SampleService.update_status(party_id, sample_id, owner, username,
                                                            publish_status=publish_status, status=SampleStatusEnum.VALID.value)
        else:
            sample_field_list = request_data["sample_field_list"]
            create_time = get_format_time()
            for sample_dict in sample_field_list:
                sample_dict["id"] = get_uuid()
                sample_dict["creator"] = username
                sample_dict["create_time"] = create_time
                sample_dict["sample_id"] = sample_id
            SampleService.delete_by_id(sample_id)
            SampleFieldsService.delete_by_sample_id(sample_id)
            sample_party_name = party_obj.party_name
            data = {
                "publish_status": publish_status,
                "owner": OwnerEnum.OTHER.value,
                "creator": username,
                "party_id": party_id,
                "party_name": sample_party_name,
                "id": sample_id,
                "name": sample_name,
                "status": publish_status,
                "sample_type": sample_type,
                "sample_count": sample_count,
                "comments": comments
            }
            SampleService.save(**data)
            SampleFieldsService.insert_many(sample_field_list)
    return get_json_result(data=True)





