
import typing


class BlockInfo:
    """
    方便传递组件的相关信息
    """

    def __init__(self):
        self.module: str = ''
        self.algo_cpt_name: str = ''  # 用于模型评估组件，识别所评估的算法组件
        self.is_algorithm: bool = False
        self.is_evaluation: bool = False
        self.task_type: str = ''
        self.need_cv: bool = False
        self.n_split: int = 0
        self.n_iter: int = 0

    def set_info(self, kw: dict):
        for k, v in kw.items():
            setattr(self, k, v)


class DictObj:
    """
    用于字典与对象间的转换

    因报告数据涉及到大量的字典操作
    故加如此类以避免大量的使用字符型键值
    """

    def load(self, args: typing.List[str], data: dict):
        for arg in args:
            setattr(self, arg, data.get(arg))

    def dump(self, args: typing.List[str]):
        return {arg: getattr(self, arg) for arg in args}


def get_model(classes: list = ()):
    # binary classes
    if len(classes) <= 2:
        return ['model_0']
    # multi classes
    else:
        return ['_'.join(('model', str(name))) for name in classes]


def get_fold(n_split: int) -> typing.List[str]:
    return [f'fold_{i}' for i in range(n_split)]
