
import copy

from federatedml.util import LOGGER
from federatedml.util import consts
from federatedml.ensemble.basic_algorithms.decision_tree.tree_core.node import Node
from federatedml.ensemble.basic_algorithms import HeteroDecisionTreeGuest


class HeteroLeafWiseDecisionTreeGuest(HeteroDecisionTreeGuest):
    """
    按叶生长(leaf-wise)的决策树

    LightGBM算法中的弱分类器
    """

    def __init__(self, tree_param):
        super(HeteroLeafWiseDecisionTreeGuest, self).__init__(tree_param)
        self.leaves = []

    def fit(self):

        LOGGER.info('fitting a guest leaf-wise decision tree')

        # Create a root node as the first leave
        self.init_packer_and_sync_gh()
        root_node = self.initialize_root_node()
        self.leaves = [root_node, ]
        self.inst2node_idx = self.assign_instance_to_root_node(self.data_bin, root_node_id=root_node.id)

        # Loop until no more leaves to split
        for dep in range(self.max_depth):
            LOGGER.info('Layer {} has {} nodes'.format(dep, len(self.leaves)))
            self.sync_cur_to_split_nodes(self.leaves, dep)
            if not self.leaves:
                break
            self.sync_node_positions(dep)
            self.update_instances_node_positions()
            split_infos = self.cal_split_info(self.leaves, dep)
            self.update_leaves(split_infos, False)
            self.assign_instances_to_new_node(dep)
        if self.leaves:
            self.assign_instance_to_leaves_and_update_weights()
        self.convert_bin_to_real()
        self.round_leaf_val()
        self.sync_tree()
        self.sample_weights_post_process()
        LOGGER.info("fitting guest leaf-wise decision tree done")

    def cal_split_info(self, leaves, dep):
        """
        计算叶节点的分裂信息
        """
        leaf_split_infos = []
        for batch_idx, i in enumerate(range(0, len(leaves), self.max_split_nodes)):
            self.cur_to_split_nodes = leaves[i: i + self.max_split_nodes]
            node_map = self.get_node_map(leaves)
            split_infos = self.compute_best_splits(self.cur_to_split_nodes, node_map, dep, batch_idx)
            leaf_split_infos.extend(split_infos)
        return leaf_split_infos

    def compute_best_splits(self, cur_to_split_nodes, node_map, dep, batch_idx):
        """
        计算当前轮次的最佳分裂节点
        """
        LOGGER.info('solving node batch {}, node num is {}'.format(batch_idx, len(cur_to_split_nodes)))
        inst2node_idx = self.get_computing_inst2node_idx()
        node_sample_count = self.count_node_sample_num(inst2node_idx, node_map)
        LOGGER.debug('sample count is {}'.format(node_sample_count))
        acc_histograms = self.get_local_histograms(dep, self.data_with_node_assignments, self.grad_and_hess,
                                                   node_sample_count, cur_to_split_nodes, node_map, ret='tensor',
                                                   hist_sub=True)

        best_split_info_guest = self.splitter.find_split(acc_histograms, self.valid_features,
                                                         self.data_bin.partitions, self.sitename,
                                                         self.use_missing, self.zero_as_missing)

        if self.complete_secure_tree:
            return best_split_info_guest

        best_splits_of_all_hosts = self.sync_host_split_infos(node_map, dep, batch_idx)

        # get encoded split-info from hosts
        final_host_split_info = self.sync_final_split_host(dep, batch_idx)
        for masked_split_info, encoded_split_info in zip(best_splits_of_all_hosts, final_host_split_info):
            for s1, s2 in zip(masked_split_info, encoded_split_info):
                s2.gain, s2.sum_grad, s2.sum_hess = s1.gain, s1.sum_grad, s1.sum_hess
        final_best_splits = self.merge_splitinfo(best_split_info_guest, final_host_split_info, need_decrypt=False)
        return final_best_splits

    def sync_host_split_infos(self, node_map, dep, batch_idx):
        """
        与所有Host方同步节点分裂信息
        """
        host_split_info_tables = self.transfer_inst.encrypted_splitinfo_host.get(idx=-1, suffix=(dep, batch_idx))
        best_splits_of_all_hosts = []

        # Sync with each party
        for host_idx, split_info_table in enumerate(host_split_info_tables):

            host_split_info = self.splitter.find_host_best_split_info(split_info_table, self.get_host_sitename(host_idx),
                                                                      self.encrypter,
                                                                      gh_packer=self.packer)
            split_info_list = [None for i in range(len(host_split_info))]
            for key in host_split_info:
                split_info_list[node_map[key]] = host_split_info[key]
            return_split_info = copy.deepcopy(split_info_list)
            for split_info in return_split_info:
                split_info.sum_grad, split_info.sum_hess, split_info.gain = None, None, None
            self.transfer_inst.federated_best_splitinfo_host.remote(return_split_info,
                                                                    suffix=(dep, batch_idx), idx=host_idx,
                                                                    role=consts.HOST)
            best_splits_of_all_hosts.append(split_info_list)
        return best_splits_of_all_hosts

    def update_leaves(self, split_infos, reach_max_depth):
        """
        更新叶节点
        """
        LOGGER.info("update {} leaf nodes".format(len(self.leaves)))
        new_leaves = []
        for i, node in enumerate(self.leaves):
            if reach_max_depth or split_infos[i].gain <= \
                    self.min_impurity_split + consts.FLOAT_ZERO:
                node.is_leaf = True
            else:
                new_leaves.extend(self.split_one_node(node, split_infos[i]))
                self.update_node_info(node, split_infos[i])
                self.update_feature_importance(split_infos[i])
            self.tree_node.append(node)
        self.leaves = new_leaves

    def split_one_node(self, node: Node, split_info):
        """
        分裂一个节点
        """
        pid = node.id
        node.left_nodeid = self.tree_node_num + 1
        node.right_nodeid = self.tree_node_num + 2
        self.tree_node_num += 2
        left_node = Node(id=node.left_nodeid,
                         sitename=self.sitename,
                         sum_grad=split_info.sum_grad,
                         sum_hess=split_info.sum_hess,
                         weight=self.splitter.node_weight(split_info.sum_grad, split_info.sum_hess),
                         is_left_node=True,
                         parent_nodeid=pid)
        right_node = Node(id=node.right_nodeid,
                          sitename=self.sitename,
                          sum_grad=node.sum_grad - split_info.sum_grad,
                          sum_hess=node.sum_hess - split_info.sum_hess,
                          weight=self.splitter.node_weight(node.sum_grad - split_info.sum_grad,
                                                           node.sum_hess - split_info.sum_hess),
                          is_left_node=False,
                          parent_nodeid=pid)
        return left_node, right_node

    def update_node_info(self, node: Node, split_info):
        """
        更新节点的描述信息
        """
        node.sitename = split_info.sitename
        if node.sitename == self.sitename:
            node.fid = self.encode("feature_idx", split_info.best_fid)
            node.bid = self.encode("feature_val", split_info.best_bid, node.id)
            node.missing_dir = self.encode("missing_dir", split_info.missing_dir, node.id)
        else:
            node.fid = split_info.best_fid
            node.bid = split_info.best_bid

    def assign_instance_to_leaves_and_update_weights(self):
        # re-assign samples to leaf nodes and update weights
        self.update_leaves([], True)
        self.update_instances_node_positions()
        self.assign_instances_to_new_node(self.max_depth, reach_max_depth=True)
