from federatedml.transfer_variable.base_transfer_variable import BaseTransferVariables


# noinspection PyAttributeOutsideInit
class BaRK_OPRF_IntersectTransferVariable(BaseTransferVariables):
    def __init__(self, flowid=0):
        super().__init__(flowid)
        # 公共的id
        self.intersect_ids = self._create_variable(name='intersect_ids',src=['guest'],dst=['host'])
        # guest方监听端口
        self.psi_listen_port = self._create_variable(name='psi_listen_port',src=['guest'],dst=['host'])
        #host生成一个jobid，方便识别不同的融合，这个和系统的jobid不一样
        self.job_id = self._create_variable(name='job_id',src=['host'],dst=['guest'])
        # guest方将自己本方样本数量发给host
        self.guest_data_num = self._create_variable(name="guest_data_num",src=["guest"],dst=["host"])
        self.guest_data_num_list = [self._create_variable(name="guest_data_num"+str(i),src=['guest'],dst=['host']) for i in range(10000)]

        # host方将自己本方样本数量发给guest

        self.host_data_num = self._create_variable(name='host_data_num', src=['host'], dst=['guest'])
        self.host_data_num_list = [self._create_variable(name="host_data_num"+str(i),src=['host'],dst=['guest']) for i in range(10000)]


        #host将每一个分片结果，是否有交集状态位发给guest
        self.intersectmd5id_list = [self._create_variable(name="intersectmd5id_"+str(i),src=['host'],dst=['guest']) for i in range(10000)]

        # host将每一个分片的实际交集结果发给guest
        self.intersectmd5id_data_list = [self._create_variable(name='intersectmd5id_data_'+str(i),src=['host'],dst=['guest'])
                                         for i in range(10000)]

        # # guest将样本进行分片，将分片数量发给host
        # self.guest_split_num = self._create_variable(name='guest_split_num', src=['guest'], dst=['host', 'arbiter'])
