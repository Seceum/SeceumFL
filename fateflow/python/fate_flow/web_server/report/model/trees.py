
import typing

from ..common import DictObj, get_model
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content


class Tree:
    """
    转换一棵树的报告数据
    """

    fate_items = [
        "splitMaskdict",  # 分裂信息
        "tree"  # 树节点数据
    ]

    fl_items = [
        "state",  # 节点
        "edg"  # 边
    ]

    fate_node_items = [
        "fid",  # 特征编号
        "id",  # 节点编号
        "isLeaf",  # 是否为页节点
        "leftNodeid",  # 左孩子节点编号
        "rightNodeid",  # 右孩子节点编号
        "sitename",  # 所属参与方名称
        "weight"  # 权重
    ]

    fl_node_items = [
        "label",  # 节点上要显示的信息
        # "class"  # TODO: no meaning yet
    ]

    def __init__(self, feature_mapping: dict):
        self.fate_data = DictObj()
        self.fl_data = DictObj()
        self._init_fl_data()
        self.feature_mapping = feature_mapping

    def _init_fl_data(self):
        self.fl_data.state = []
        self.fl_data.edg = []

    def convert(self, tree_data: dict):
        self.fate_data.load(self.fate_items, tree_data)
        for node_data in self.fate_data.tree:
            node, edge = self._get_node_and_edge(node_data)
            self.fl_data.state.append(node)
            self.fl_data.edg.extend(edge)
        return self.fl_data.dump(self.fl_items)

    def _get_node_and_edge(self, node_data: dict):
        fate_node = DictObj()
        fate_node.load(self.fate_node_items, node_data)
        return self._convert_fl_node(fate_node),\
               self._convert_fl_edge(fate_node)

    def _convert_fl_node(self, fate_node):
        fl_node = DictObj()
        if fate_node.isLeaf:
            fl_node.label = self._gen_label(fate_node.id, fate_node.sitename,
                                            weight=fate_node.weight)
        else:
            fid = str(fate_node.fid)
            feature = self.feature_mapping.get(fid)
            split = self.fate_data.splitMaskdict.get(fid)
            fl_node.label = self._gen_label(fate_node.id, fate_node.sitename,
                                            feature=feature, split=split)
        return fl_node.dump(self.fl_node_items)

    def _convert_fl_edge(self, fate_node):
        edges = []
        if not fate_node.isLeaf:
            edges.append(self._gen_edge(fate_node.id, fate_node.leftNodeid))
            edges.append(self._gen_edge(fate_node.id, fate_node.rightNodeid))
        return edges

    @staticmethod
    def _gen_edge(start: int, end: int):
        return {
            "start": start,  # 起始节点编号
            "end": end,  # 终止节点编号
            # "option": {}  # TODO: no meaning yet
        }

    @staticmethod
    def _gen_label(node_id: int, site_name: str, feature: str = None,
                   split: float = None, weight: float = None):
        id_info = f'id: {node_id}'
        if weight:
            split_info = f'weight: {weight}'
            return '\n'.join((id_info, split_info, site_name))
        elif feature and split:
            split_info = f'{feature} <= {split}'
            return '\n'.join((id_info, split_info, site_name))
        else:
            return '\n'.join((id_info, site_name))


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.trees)
class Trees(Converter):
    """
    树模型报告数据转换
    """

    @property
    def fate_items(self) -> typing.List[str]:
        return [
            "treeDim",  # 模型数量
            "treeNum",  # 树的总数量
            "trees",  # 每棵树的数据
            "classes",  # 类别名称
            "featureNameFidMapping",  # 特征名称映射
        ]

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            "treeDim",  # 模型数量
            "treeNum",  # 树的总数量
            "iteration",  # 每个模型中的树数量，对应进度条方块个数
            "model",  # 模型名称列表 长度为treeDim
            "data",  # 树形图数据 长度为treeNum
        ]

    # def convert(self, fate_data: DictObj, fl_data: DictObj):
    #     self._convert_tree_info(fate_data, fl_data)
    #     for tree_data in fate_data.trees:
    #         tree = Tree(fate_data.featureNameFidMapping)
    #         fl_data.data.append(tree.convert(tree_data))  # TODO
    #
    # @staticmethod
    # def _convert_tree_info(fate_data: DictObj, fl_data: DictObj):
    #     fl_data.data = []
    #     fl_data.treeDim = fate_data.treeDim
    #     fl_data.treeNum = fate_data.treeNum
    #     fl_data.iteration = fl_data.treeNum // fl_data.treeDim
    #     fl_data.model = get_model(fate_data.classes)

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._convert_tree_info(fate_data, fl_data)
        for i, model in enumerate(fl_data.model):
            model_trees = []
            for j in range(fl_data.iteration):
                tree_data = fate_data.trees[i * fl_data.iteration + j]
                tree = Tree(fate_data.featureNameFidMapping)
                model_trees.append(tree.convert(tree_data))
            fl_data.data[model] = model_trees

    @staticmethod
    def _convert_tree_info(fate_data: DictObj, fl_data: DictObj):
        fl_data.data = {}
        fl_data.treeDim = fate_data.treeDim
        fl_data.treeNum = fate_data.treeNum
        fl_data.iteration = fl_data.treeNum // fl_data.treeDim
        fl_data.model = get_model(fate_data.classes)
