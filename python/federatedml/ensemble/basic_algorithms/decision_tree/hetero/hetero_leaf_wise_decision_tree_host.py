
import numpy as np

from federatedml.util import consts
from federatedml.util import LOGGER
from federatedml.ensemble.basic_algorithms import HeteroDecisionTreeHost


class HeteroLeafWiseDecisionTreeHost(HeteroDecisionTreeHost):
    """
    按叶生长(leaf-wise)的决策树

    作为LightGBM算法中的弱分类器
    """

    def __init__(self, tree_param):
        super(HeteroLeafWiseDecisionTreeHost, self).__init__(tree_param)
        self.leaves = []

    def fit(self):

        LOGGER.info('fitting a host leaf-wise decision tree')

        self.init_compressor_and_sync_gh()
        LOGGER.debug('grad and hess count {}'.format(self.grad_and_hess.count()))

        # Loop until no more leaves to split
        for dep in range(self.max_depth):
            self.sync_leaf_nodes(dep)
            LOGGER.info('Layer {} has {} nodes'.format(dep, len(self.leaves)))
            self.generate_split_point_masking_variable(dep)
            if len(self.leaves) == 0:
                break
            self.inst2node_idx = self.sync_node_positions(dep)
            self.update_instances_node_positions()
            self.cal_split_info(dep)
            dispatch_node_host = self.sync_dispatch_node_host(dep)
            self.assign_instances_to_new_node(dispatch_node_host, dep=dep)
        self.sync_tree()
        self.convert_bin_to_real(decode_func=self.decode, split_maskdict=self.split_maskdict)
        LOGGER.info("fitting host leaf-wise decision tree done")

    def cal_split_info(self, dep):
        """
        计算叶节点的分裂信息
        """
        for batch_idx, i in enumerate(range(0, len(self.leaves), self.max_split_nodes)):
            self.cur_to_split_nodes = self.leaves[i: i + self.max_split_nodes]
            node_map = self.get_node_map(self.cur_to_split_nodes)
            self.compute_best_splits(self.cur_to_split_nodes, node_map=node_map, dep=dep, batch=batch_idx)

    def sync_leaf_nodes(self, dep=-1):
        """
        与Guest方同步叶节点
        """
        LOGGER.info("get leaf nodes of layer {}".format(dep))
        self.leaves = self.transfer_inst.tree_node_queue.get(idx=0, suffix=(dep,))

    def compute_best_splits(self, cur_to_split_nodes: list, node_map, dep, batch):
        """
        计算当前轮次的最佳分裂节点
        """
        LOGGER.info('solving node batch {}, node num is {}'.format(batch, len(cur_to_split_nodes)))
        if not self.complete_secure_tree:
            data = self.data_with_node_assignments
            inst2node_idx = self.get_computing_inst2node_idx()
            node_sample_count = self.count_node_sample_num(inst2node_idx, node_map)
            LOGGER.debug('sample count is {}'.format(node_sample_count))
            acc_histograms = self.get_local_histograms(dep, data, self.grad_and_hess, node_sample_count,
                                                       cur_to_split_nodes, node_map, ret='tb',
                                                       hist_sub=True)

            split_info_table = self.splitter.host_prepare_split_points(histograms=acc_histograms,
                                                                       use_missing=self.use_missing,
                                                                       valid_features=self.valid_features,
                                                                       sitename=self.sitename,
                                                                       left_missing_dir=self.missing_dir_mask_left[dep],
                                                                       right_missing_dir=self.missing_dir_mask_right[dep],
                                                                       mask_id_mapping=self.fid_bid_random_mapping,
                                                                       batch_size=self.bin_num,
                                                                       cipher_compressor=self.cipher_compressor,
                                                                       shuffle_random_seed=np.abs(hash((dep, batch)))
                                                                       )
            self.sync_host_split_infos(split_info_table, dep, batch)
        else:
            LOGGER.debug('skip splits computation')

    def sync_host_split_infos(self, split_info_table, dep, batch):
        """
        与Guest方同步本方节点分裂信息
        """
        suffix = (dep, batch)
        self.transfer_inst.encrypted_splitinfo_host.remote(split_info_table, role=consts.GUEST, idx=-1, suffix=suffix)
        best_split_info = self.transfer_inst.federated_best_splitinfo_host.get(suffix=suffix, idx=0)
        unmasked_split_info = self.unmask_split_info(best_split_info, self.inverse_fid_bid_random_mapping,
                                                     self.missing_dir_mask_left[dep], self.missing_dir_mask_right[dep])
        return_split_info = self.encode_split_info(unmasked_split_info)
        self.transfer_inst.final_splitinfo_host.remote(return_split_info, role=consts.GUEST, idx=-1, suffix=suffix)
