import time

from federatedml.statistic.intersect.bark_oprf_intersect.bark_oprf_intersect_base import BaRK_OPRF_Intersection
from federatedml.util import consts, LOGGER
from federatedml.util.data_compress_decompress import zlibcompress,zlibdecompress_dataframe
from math import ceil,sqrt
import multiprocessing
import os
import pandas as pd
import gc
from fate_arch.session import computing_session as session
from federatedml.feature.instance import Instance
import uuid
from pathlib import Path
from fate_arch.common import file_utils, conf_utils
from fate_arch.common.conf_utils import SERVICE_CONF
from fate_arch.common.conf_utils import get_base_config
import subprocess
import copy

class BaRK_OPRF_IntersectGuest(BaRK_OPRF_Intersection):
    def __init__(self):
        super().__init__()
        self.role = consts.GUEST

    def bark_oprf_calculation_process(self,data_instance1):
        LOGGER.info("guest bark oprf content {}".format(get_base_config("bark_oprf")))
        port = int(get_base_config("bark_oprf")["port"])
        job_id_list = self.transfer_variable.job_id.get(idx=-1)
        self.base_rows = data_instance1.count()
        self.transfer_variable.guest_data_num.remote(self.base_rows,role=consts.HOST,idx=-1)
        host_data_num_list = self.transfer_variable.host_data_num.get(idx=-1)
        # 计算分片大小
        tempmaxlist = [max(self.base_rows,host_data_num) for host_data_num in host_data_num_list]
        stopvaluelist = [self.cal_stopvalue(tempmax) for tempmax in tempmaxlist]
        split_size_list = [self.getchildren(tempmaxlist[i],stopvaluelist[i]) for i in range(0,len(tempmaxlist))]
        # 分片数量
        split_numlist = [tempmaxlist[i] / split_size_list[i] for i in range(0,len(tempmaxlist))]
        #样本数量为质数
        for i in range(0,len(split_numlist)):
            if split_numlist[i] == tempmaxlist[i]:
                split_numlist[i] = int(ceil(tempmaxlist[i] / stopvaluelist[i]))
                if split_numlist[i] % 2 == 1:
                    split_numlist[i] = split_numlist[i] + 1

        cpuPoolSizelist = [multiprocessing.cpu_count() for _ in range(0,len(self.host_party_id_list))]
        start = time.time()
        data_instance = self.data_format_convert_to_dataframe(data_instance1)
        end = time.time()
        LOGGER.info("extract id cost time----{}".format(end-start))
        data_instancelist = [None for i in range(len(self.host_party_id_list))]
        start = time.time()
        if self.need_encrypt:
            LOGGER.info('guest id encrypt start--{}'.format(split_numlist[0]))
            for i in range(len(self.host_party_id_list)):
                data_instancelist[i] = self.id_encrypt(split_numlist[i],cpuPoolSizelist[i],copy.deepcopy(data_instance))

        end = time.time()
        LOGGER.info("id encrypt cost time---{}".format(end-start))
        #交集结果存储
        psi_store_data_dirlist = ['/data/psi'+str(i)+'/data/' for i in range(len(self.host_party_id_list))]
        for psi_store_data_dir in psi_store_data_dirlist:
            if os.path.isdir(psi_store_data_dir):
                pass
            else:
                os.makedirs(psi_store_data_dir)

        # 每一个host方和guest方监听端口要一致，
        psi_listen_portlist = [port + i * 1 for i in range(0,len(self.host_party_id_list))]
        LOGGER.info("psi listen portlis----{}".format(psi_listen_portlist))
        #guest将对应host方端口发给host
        for i in range(0,len(self.host_party_id_list)):
            self.transfer_variable.psi_listen_port.remote(psi_listen_portlist[i],role=consts.HOST,idx=i)

        # 针对多个host，guest方数据进行分片
        # 下面为串行分片方法
        f = 1
        if f == 0:
            for index in range(0,len(self.host_party_id_list)):
                job_id = job_id_list[index]
                split_num = split_numlist[index]
                host_data_num = host_data_num_list[index]
                data_instance = data_instancelist[index]
                psi_store_data_dir = psi_store_data_dirlist[index]

                # 不需要分片
                if split_num == 1:
                    if self.base_rows < host_data_num:
                        t = ceil(host_data_num / self.base_rows)
                        t = ceil(sqrt(t))
                        for i in range(int(t)+1):
                            data_instance = pd.concat([data_instance,data_instance],axis=0)
                        data_instance.reset_index(inplace=True,drop=True)
                        data_instance = data_instance.loc[0:(host_data_num-1),:]
                        # add by tjx 202242
                        mask = pd.DataFrame(data_instance['md5']).apply(pd.Series.duplicated, axis=0)
                        data_instance['md5'] = pd.DataFrame(data_instance['md5']).mask(mask, None)
                        data_instance['md5'] = data_instance['md5'].apply(
                            lambda x: ''.join(str(uuid.uuid4()).split('-')) if x == None else x)

                    path = ''.join([psi_store_data_dir, job_id,'_',str(0), '.parquet'])
                    pd.DataFrame(data_instance['md5'], columns=['md5']).to_parquet(path, index=False,engine='fastparquet')
                    LOGGER.info('guest save md5 data')
                    path = ''.join([psi_store_data_dir,job_id,'_', 'data', '_', str(0), '.parquet'])
                    data_instance.to_parquet(path, index=False, engine='fastparquet')
                    LOGGER.info('guest save origin data')

                else:#需要分片
                    for i in range(0,int(split_num)):
                        try:
                            data = data_instance.loc[(data_instance['md5lastpos']==i),:]
                        except:
                            continue
                        datalen = len(data)
                        self.transfer_variable.guest_data_num_list[i].remote(datalen, role=consts.HOST, idx=index)
                        host_data_num = self.transfer_variable.host_data_num_list[i].get(idx=index)
                        LOGGER.info('get split data num from host {}'.format(host_data_num))
                        # 当其中一方数据量为0，则肯定没有交集该分片数据

                        if datalen == 0 or host_data_num == 0:
                            continue

                        if datalen < host_data_num:
                            t = ceil(host_data_num / datalen)
                            t = ceil(sqrt(t))
                            for j in range(int(t)+1):
                                data = pd.concat([data,data],axis=0)
                            data.reset_index(inplace=True,drop=True)
                            data = data.loc[0:(host_data_num-1),:]
                            # add by tjx 202242
                            mask = pd.DataFrame(data['md5']).apply(pd.Series.duplicated, axis=0)
                            data['md5'] = pd.DataFrame(data['md5']).mask(mask, None)
                            data['md5'] = data['md5'].apply(
                                lambda x: ''.join(str(uuid.uuid4()).split('-')) if x == None else x)

                        path = ''.join([psi_store_data_dir,job_id,'_', str(i), '.parquet'])
                        pd.DataFrame(data['md5'], columns=['md5']).to_parquet(path, index=False, engine='fastparquet')
                        path = ''.join([psi_store_data_dir,job_id,'_', 'data', '_', str(i), '.parquet'])
                        if 'md5' in data.columns:
                            del data['md5']
                            gc.collect()

                        data.to_parquet(path, index=False, engine='fastparquet')

        # 并行方法
        elif f == 1:
            LOGGER.info('split data parallel')
            [self.split_data(job_id_list[i],split_numlist[i],host_data_num_list[i],data_instancelist[i],psi_store_data_dirlist[i],
                             self.base_rows,i) for i in range(len(self.host_party_id_list))]

        # psi算法路径
        bark_oprf_exe_dir = '/opt/BaRK-OPRF/Release/bOPRFmain.exe'
        # 计算psi psi并行数量，最大为split num的一半
        split_size1list = [self.getchildren(split_numlist[i],split_numlist[i]/2) if split_numlist[i] >= multiprocessing.cpu_count() and tempmaxlist[i]>60000000 else int(split_numlist[i])
                           for i in range(0,len(self.host_party_id_list))]

        # psi 并行计算
        f = 0
        # 下面为串行
        if f == 0:
            for index in range(0,len(self.host_party_id_list)):
                job_id = job_id_list[index]
                split_num = split_numlist[index]
                split_size1 = int(split_size1list[index])
                psi_store_data_dir = psi_store_data_dirlist[index]
                psi_listen_port = psi_listen_portlist[index]
                cpuPoolSize = cpuPoolSizelist[index]

                if split_num > 1:
                    LOGGER.info('guest psi parallel compute start')
                    self.psi_parallel_compute(split_num,split_size1,psi_store_data_dir,bark_oprf_exe_dir,psi_listen_port,
                                      cpuPoolSize,job_id)
                    LOGGER.info('guest psi parallel compute finish')
                    #串行接收id
                    for i in range(0,int(split_num)):
                        flag = self.transfer_variable.intersectmd5id_list[i].get(idx=index)
                        if not flag :
                            continue
                        arr_id = self.transfer_variable.intersectmd5id_data_list[i].get(idx=index)
                        arr_id = zlibdecompress_dataframe(arr_id)
                        arr_id = arr_id.applymap(lambda  x:str(x))
                        # 数据筛选
                        path = ''.join([psi_store_data_dir, job_id,'_','data', '_', str(i), '.parquet'])
                        guest_data1 = pd.read_parquet(path, engine='fastparquet')
                        arr_id.set_index('id', inplace=True)
                        temp = guest_data1.merge(arr_id, how='inner', left_on=['id'], right_index=True)

                        path1 = ''.join([psi_store_data_dir, job_id,'_', 'inter', str(i), '.parquet'])
                        temp.to_parquet(path1,
                                index=False, engine='fastparquet')

                elif split_num == 1:#psi串行计算
                    LOGGER.info("guest psi----------dafddfff")
                    for i in range(0,int(split_num)):
                        path = ''.join([psi_store_data_dir,job_id,'_', str(i), '.parquet'])
                        if not os.path.exists(path):
                            continue

                        command = ''.join([bark_oprf_exe_dir, " -r 0 ", path, " -ip ", '0.0.0.0:', str(psi_listen_port)])
                        LOGGER.info("guest command------{}".format(command))
                        LOGGER.info("path--env---{}".format(os.getenv("PATH")))
                        try:
                            os.system(command)
                        except Exception as e:
                            LOGGER.info("error----{}".format(e))
                        flag = self.transfer_variable.intersectmd5id_list[i].get(idx=index)
                        if not flag:
                            continue

                        arr_id = self.transfer_variable.intersectmd5id_data_list[i].get(idx=index)
                        arr_id = zlibdecompress_dataframe(arr_id)
                        arr_id = arr_id.applymap(lambda x:str(x))

                        # 数据筛选
                        path = ''.join([psi_store_data_dir, job_id, '_', 'data', '_', str(i), '.parquet'])
                        guest_data1 = pd.read_parquet(path, engine='fastparquet')
                        arr_id.set_index('id', inplace=True)
                        temp = guest_data1.merge(arr_id, how='inner', left_on=['id'], right_index=True)

                        path1 = ''.join([psi_store_data_dir, job_id, '_', 'inter', str(i), '.parquet'])
                        temp.to_parquet(path1,
                                    index=False, engine='fastparquet')

        # 多方psi并行计算 通信方面不能并行
        elif f == 1:
            LOGGER.info('psi compute parallel')
            [self.psi_compute(job_id_list[i],split_numlist[i],split_size1list[i],psi_store_data_dirlist[i],psi_listen_portlist[i],
                              cpuPoolSizelist[i],i,bark_oprf_exe_dir) for i in range(len(self.host_party_id_list))]



        #读取每一个交集结果的子集
        LOGGER.info("guest zhixing finish----------------")
        guest_datalist = [pd.DataFrame() for i in range(len(self.host_party_id_list))]
        for index in range(0,len(self.host_party_id_list)):
            split_num = split_numlist[index]
            psi_store_data_dir = psi_store_data_dirlist[index]
            guest_data = guest_datalist[index]
            job_id = job_id_list[index]

            # 串行读取数据
            f = 1
            if f == 0:
                for i in range(0,int(split_num)):
                    path = ''.join([psi_store_data_dir, job_id,'_','inter', str(i), '.parquet'])
                    if os.path.exists(path):
                        if len(guest_data) == 0:
                            guest_data = pd.read_parquet(path, engine='fastparquet')
                        else:
                            guest_data = guest_data.append(pd.read_parquet(path, engine='fastparquet'))
            # 并行读取数据
            elif f == 1:
                LOGGER.info('parallel read data-----')
                guest_data = self.parallel_read_data(psi_store_data_dir,job_id,split_num)

            guest_data.drop_duplicates(subset=['id'],keep='first',inplace=True)
            if 'md5' in guest_data.columns:
                del guest_data['md5']
            if 'md5id' in guest_data.columns:
                del guest_data['md5id']
            if 'md5lastpos' in guest_data.columns:
                del guest_data['md5lastpos']

            # 最终结果自己本方的数据集
            guest_data.reset_index(drop=True,inplace=True)
            #guest和host每一方的交集结果
            guest_datalist[index] = guest_data

        #需要将guest data list中进行求交得到最终的结果
        guest_data = guest_datalist[0]
        for i in range(1,len(guest_datalist)):
            guest_data = guest_data.merge(guest_datalist[i],on=['id'],how='inner')
        guest_data.reset_index(drop=True,inplace=True)

        #将结果转换为table
        f = 0
        #串行转换
        if f == 0:
            data_in = [(str(guest_data.loc[index, 'id']), guest_data.loc[index, 'id']) for index in guest_data.index]
        else:
            data_in = self.parallel_convert_table(multiprocessing.cpu_count(),guest_data)
            for i in data_in:
                LOGGER.info("i content-----{}".format(i))

        guest_data = session.parallelize(data_in, include_key=True, partition=4)
        if self.sync_intersect_ids:
            self.transfer_variable.intersect_ids.remote(guest_data, role=consts.HOST, idx=-1)

        return guest_data