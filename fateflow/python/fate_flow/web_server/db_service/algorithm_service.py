from fate_flow.web_server.db.db_models import StudioAlgorithmInfo,StudioSampleAlgorithm
from fate_flow.web_server.db_service.common_service import CommonService


class AlgorithmInfoService(CommonService):
    model = StudioAlgorithmInfo


class SampleAlgorithmService(CommonService):
    model = StudioSampleAlgorithm

