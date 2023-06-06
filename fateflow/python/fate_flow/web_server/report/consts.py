
from enum import Enum, unique, auto


@unique
class CollectorEnum(Enum):
    """
    对应Collector类的子类
    """

    # TODO: 报告全部开发完成后应该移除此项
    dummy = auto()  # 用于Mock数据

    # add by tjx 20220624
    db_data = auto()
    # add by tjx 20220811
    db_data2 = auto()
    db_data3 = auto()
    # add by tjx 20220819
    data1 = auto()

    data = auto()
    model = auto()
    metric = auto()
    cv_metric = auto()
    iter_metric = auto()


@unique
class LoaderEnum(Enum):
    """
    对应Loader类的子类
    """

    # TODO: 报告全部开发完成后应该移除此项
    dummy = auto()  # 用于Mock数据

    normal = auto()
    metric = auto()
    evaluation = auto()
