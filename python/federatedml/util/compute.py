import numpy as np
import functools
from typing import List
from federatedml.ensemble.boosting.hetero.hetero_secureboost_guest import HeteroSecureBoostingTreeGuest
# from federatedml.ensemble.basic_algorithms.decision_tree.hetero.hetero_lightGBM_decision_tree_guest import HeteroDecisionTreeLeafWiseGuest
# from federatedml.ensemble.basic_algorithms.decision_tree.hetero.hetero_lightGBM_decision_tree_host import HeteroDecisionTreeLeafWiseHost

from federatedml.ensemble.boosting.boosting_core.boosting import Boosting


def fun3_1(host_leaf_pos_list,guest_leaf_pos):
    for host_leaf_pos in host_leaf_pos_list:
        guest_leaf_pos = guest_leaf_pos.join(host_leaf_pos, merge_leaf_pos)

    return guest_leaf_pos

def merge_leaf_pos(pos1, pos2):
    return pos1 + pos2

# def fun2_1(trees,data_inst,node_pos):
#     traverse_func = functools.partial(traverse_guest_local_trees, trees=trees)
#     guest_leaf_pos = node_pos.join(data_inst, traverse_func)
#     return guest_leaf_pos

# def traverse_guest_local_trees(node_pos, sample, trees: List[HeteroDecisionTreeLeafWiseGuest]):
#
#     """
#         in mix mode, a sample can reach leaf directly
#     """
#     new_node_pos = node_pos + 0  # avoid inplace manipulate
#     for t_idx, tree in enumerate(trees):
#
#         cur_node_idx = new_node_pos[t_idx]
#
#         if not tree.use_guest_feat_only_predict_mode:
#             continue
#
#         rs, reach_leaf = HeteroSecureBoostingTreeGuest.traverse_a_tree(tree, sample, cur_node_idx)
#         new_node_pos[t_idx] = rs
#
#     return new_node_pos

# def fun1_1(trees,node_pos,data_inst):
#     local_traverse_func = functools.partial(traverse_host_local_trees, trees=trees)
#     leaf_pos = node_pos.join(data_inst, local_traverse_func)
#     return leaf_pos
#
#
# def traverse_host_local_trees(node_pos, sample, trees: List[HeteroDecisionTreeLeafWiseHost]):
#
#     """
#     in mix mode, a sample can reach leaf directly
#     """
#     new_node_pos = node_pos + 0
#     for i in range(len(trees)):
#
#         tree = trees[i]
#         if len(tree.tree_node) == 0:  # this tree belongs to other party because it has no tree node
#             continue
#         leaf_id = tree.host_local_traverse_tree(sample, tree.tree_node, use_missing=tree.use_missing,
#                                                     zero_as_missing=tree.zero_as_missing)
#         new_node_pos[i] = leaf_id
#
#     return new_node_pos

def fun1(data_inst,tree_num):
    return data_inst.mapValues(lambda x: np.zeros(tree_num, dtype=np.int64))



def fun2(data_in_table):
    return  data_in_table.mapValues(lambda row: Boosting.data_format_transform(row))


def fun3(cur_sample_weights):
    return cur_sample_weights.map(lambda x, y: (int(x), y))


def fun4(grad_and_hess, data_with_sample_weight):
    return grad_and_hess.join(data_with_sample_weight,lambda v1, v2: (v1[0] * v2.weight, v1[1] * v2.weight))


def fun5(y, y_hat,loss_method):
    return y.join(y_hat, lambda y, f_val: \
          (loss_method.compute_grad(y, loss_method.predict(f_val)), \
          loss_method.compute_hess(y, loss_method.predict(f_val))))


def fun6(y, y_hat,loss_method):
    return  y.join(y_hat, lambda y, f_val:
    (loss_method.compute_grad(y, f_val),
     loss_method.compute_hess(y, f_val)))


def fun7(g_h,dim):
    return g_h.mapValues(
            lambda grad_and_hess: (grad_and_hess[0][dim], grad_and_hess[1][dim]))


def fun8(predict_result, predict_cache):
    return  predict_result.join(predict_cache, lambda v1, v2: v1 + v2)


def fun9(data_inst, tree_num):
    return data_inst.mapValues(lambda x: np.zeros(tree_num, dtype=np.int64) + np.nan)


def fun10(node_pos_tb):
    return  node_pos_tb.filter(lambda key, value: value['reach_leaf_node'].all())


