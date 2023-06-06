import pandas as pd

from fate_flow.web_server.db_service.sample_service import SampleFieldsService, SampleService
from fate_flow.web_server.utils.enums import FusionFieldControl, FieldTypeChinese, MixTypeChineseEnum


def get_field_info_df(sample_list, job_type, **kwargs):
    sample_fusion_info = SampleService.query(filters=[SampleService.model.id.in_(sample_list)],
                                             cols=[SampleService.model.id.alias(
                                                 "sample_id"), SampleService.model.name.alias("sample_name"),
                                                 SampleService.model.party_name,
                                                 SampleService.model.party_id,
                                                 SampleService.model.sample_count]).dicts()
    party_info_dict = {i["sample_id"]: (i["party_id"], i["party_name"]) for i in sample_fusion_info}
    cols = [SampleFieldsService.model.id.alias("field_id"),
            SampleFieldsService.model.field_examples,
            SampleFieldsService.model.sample_id, SampleFieldsService.model.field_name,
            SampleFieldsService.model.field_type, SampleFieldsService.model.field_sort,
            SampleFieldsService.model.distribution_type, SampleFieldsService.model.data_type,
            SampleFieldsService.model.field_description, SampleFieldsService.model.positive_value,
            SampleService.model.party_id, SampleService.model.party_name]
    feature_info_list = list(SampleFieldsService.get_by_sample_info(sample_list, cols, **kwargs).dicts())
    for feature_info in feature_info_list:
        feature_info["party_id"] = party_info_dict[feature_info["sample_id"]][0]
        feature_info["party_name"] = party_info_dict[feature_info["sample_id"]][1]
    if feature_info_list:
        df = pd.DataFrame(feature_info_list)
        if job_type == MixTypeChineseEnum.union.value:
            df.drop_duplicates(subset='field_name', keep='first', inplace=True)
    else:
        df = pd.DataFrame()
    return df


def get_fusion_fields(party_info, job_type, module_name=None, **kwargs):
    if module_name == "SecureInformationRetrieval":
        sample_list = [host_info["sample_id"] for host_info in party_info["host"]]
    else:
        sample_infos = party_info["host"]
        sample_infos.insert(0, party_info["guest"])
        sample_list = [i["sample_id"] for i in sample_infos]
    df = get_field_info_df(sample_list, job_type, **kwargs)
    if not df.empty and module_name:
        field_type = getattr(FusionFieldControl, module_name, "")
        if field_type != "all":
            query_field_type = getattr(FieldTypeChinese, field_type, "")
            df = df[df.distribution_type == query_field_type]
        sample_list = df.to_dict("records")
    else:
        sample_list = df.to_dict("records")
    return sample_list
