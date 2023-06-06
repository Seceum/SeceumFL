from federatedml.statistic.intersect import Intersect
from federatedml.transfer_variable.transfer_class.bark_oprf_transfer_variable import BaRK_OPRF_IntersectTransferVariable
from federatedml.util import consts, LOGGER
from math import ceil
from joblib import Parallel,delayed
from functools import partial
import pandas as pd
import gc
import hashlib
import os
import uuid
from math import sqrt


class BaRK_OPRF_Intersection(Intersect):
    def __init__(self):
        super().__init__()
        self.transfer_variable = BaRK_OPRF_IntersectTransferVariable()
        self.base_rows = 0
        self.role = None

    def load_params(self, param):
        super().load_params(param=param)
        self.bark_oprf_params = param.bark_oprf_params
        self.encrypt_method = self.bark_oprf_params.encrypt_method
        self.need_encrypt = self.bark_oprf_params.need_encrypt

    def get_intersect_method_meta(self):
        bark_oprt_meta = {"intersect_method": self.intersect_method,
                    "encrypt_method": self.bark_oprf_params.encrypt_method,
                    "need_encrypt": self.bark_oprf_params.need_encrypt}
        return bark_oprt_meta

    def run_intersect(self, data_instances):
        LOGGER.info("Start BaRK-OPRF Intersection")
        intersect_ids = self.bark_oprf_calculation_process(data_instances)
        return intersect_ids

    def bark_oprf_calculation_process(self, data_instances):
        raise NotImplementedError("This method should not be called here")

    def cal_stopvalue(self,tempmax):
        if tempmax<=5000000:
            return 500000
        elif tempmax>5000000 and tempmax <= 100000000:
            return 2500000
        else:
            return 5000000

    def getchildren(self,num, stopvalue):
        list = []
        a = 1
        while a <= num:
            if num % a == 0:
                list.append(a)
                if a >= stopvalue:
                    break
            a += 1

        return list[-2] if list[-1] > stopvalue else list[-1]

    def stringtomd5(self,originstr):
        signaturemd5 = hashlib.md5()
        signaturemd5.update(originstr.encode('utf-8'))
        return signaturemd5.hexdigest()

    def data_format_convert_to_dataframe(self,data_instance1):
        data_instance = pd.DataFrame(data_instance1.collect())
        data_instance.columns = ['id','features']
        return pd.DataFrame(data_instance.loc[:,"id"],columns=['id'])

    def func(self,data,split_num):
        data["id"] = data['id'].astype(str)
        data.insert(0,'md5',None)
        data['md5'] = data['id'].apply(lambda x:self.stringtomd5(x))
        data['md5lastpos'] = data['md5'].apply(lambda x:int(ord(x[-1]) % split_num))
        return data

    # 数据分片
    def split_data(self,job_id_list,split_numlist,host_data_num_list,data_instancelist,
                                         psi_store_data_dirlist,base_rows,index):
        job_id = job_id_list
        split_num = split_numlist
        host_data_num = host_data_num_list
        data_instance = data_instancelist
        psi_store_data_dir = psi_store_data_dirlist
        # 不需要分片
        if split_num == 1:
            if base_rows < host_data_num:
                t = ceil(host_data_num / base_rows)
                t = ceil(sqrt(t))
                for i in range(int(t)+1):
                    data_instance = pd.concat([data_instance, data_instance], axis=0)
                data_instance.reset_index(inplace=True, drop=True)
                data_instance = data_instance.loc[0:(host_data_num - 1), :]
                # add by tjx 202242
                mask = pd.DataFrame(data_instance['md5']).apply(pd.Series.duplicated, axis=0)
                data_instance['md5'] = pd.DataFrame(data_instance['md5']).mask(mask, None)
                data_instance['md5'] = data_instance['md5'].apply(lambda x: ''.join(str(uuid.uuid4()).split('-')) if x == None else x)


            path = ''.join([psi_store_data_dir, job_id, '_', str(0), '.parquet'])
            pd.DataFrame(data_instance['md5'], columns=['md5']).to_parquet(path, index=False, engine='fastparquet')
            path = ''.join([psi_store_data_dir, job_id, '_', 'data', '_', str(0), '.parquet'])
            data_instance.to_parquet(path, index=False, engine='fastparquet')
            LOGGER.info('guest save origin data')

        else:  # 需要分片
            for i in range(0, int(split_num)):
                try:
                    data = data_instance.loc[(data_instance['md5lastpos'] == i), :]
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
                        data = pd.concat([data, data], axis=0)
                    data.reset_index(inplace=True, drop=True)
                    data = data.loc[0:(host_data_num - 1), :]
                    # add by tjx 202242
                    mask = pd.DataFrame(data['md5']).apply(pd.Series.duplicated,axis=0)
                    data['md5']=pd.DataFrame(data['md5']).mask(mask,None)
                    data['md5']=data['md5'].apply(lambda x: ''.join(str(uuid.uuid4()).split('-')) if x==None else x)

                path = ''.join([psi_store_data_dir, job_id, '_', str(i), '.parquet'])
                pd.DataFrame(data['md5'], columns=['md5']).to_parquet(path, index=False, engine='fastparquet')
                path = ''.join([psi_store_data_dir, job_id, '_', 'data', '_', str(i), '.parquet'])
                if 'md5' in data.columns:
                    del data['md5']

                data.to_parquet(path, index=False, engine='fastparquet')


    # 并行对数据进行分片
    def split_data_parallel(self,len_host_party,job_id_list,split_numlist,host_data_num_list,data_instancelist,
                                     psi_store_data_dirlist,base_rows):

        with Parallel(n_jobs=int(len_host_party),backend='multiprocessing') as p:
            lamdfun2P = partial(self.split_data)
            lld2 = p(
                delayed(lamdfun2P)(job_id_list[index:index+1],split_numlist[index:index+1],host_data_num_list[index:index+1],data_instancelist[index:index+1],
                                   psi_store_data_dirlist[index:index+1],base_rows,index) for index in
                range(0, int(len_host_party)))

    # host数据进行分片
    def host_split_data(self,data,job_id,i,psi_store_data_dir):
        datalen = len(data)
        self.transfer_variable.host_data_num_list[i].remote(datalen, role=consts.GUEST, idx=0)
        guest_data_num = self.transfer_variable.guest_data_num_list[i].get(idx=0)
        # 当其中一方没有数据
        if datalen == 0 or guest_data_num == 0:
            return
        if datalen < guest_data_num:
            t = ceil(guest_data_num / datalen)
            t = ceil(sqrt(t))
            for j in range(int(t) + 1):
                data = pd.concat([data, data], axis=0)
            data.reset_index(inplace=True, drop=True)
            data = data.loc[0:(guest_data_num - 1), :]
            # add by tjx 202242
            mask = pd.DataFrame(data['md5']).apply(pd.Series.duplicated, axis=0)
            data['md5'] = pd.DataFrame(data['md5']).mask(mask, None)
            data['md5'] = data['md5'].apply(
                lambda x: ''.join(str(uuid.uuid4()).split('-')) if x == None else x)


        path = ''.join([psi_store_data_dir, job_id, '_', str(i), '.parquet'])
        pd.DataFrame(data['md5'], columns=['md5']).to_parquet(path, index=False, engine='fastparquet')
        path = ''.join([psi_store_data_dir, job_id, '_', 'data', '_', str(i), '.parquet'])
        if 'flag' in data.columns:
            del data['flag']
        if 'md5lastpos' in data.columns:
            del data['md5lastpos']

        data.to_parquet(path, index=False, engine='fastparquet')
        LOGGER.info('host save split data')

    # host对数据进行并行分片
    def host_split_data_parallel(self,split_num, data_instance, job_id,psi_store_data_dir):
        with Parallel(n_jobs=int(split_num),backend='multiprocessing') as p:
            lamdfun2P = partial(self.host_split_data)
            lld2 = p(
                delayed(lamdfun2P)(data_instance.loc[(data_instance['md5lastpos']==i),:],job_id, i,psi_store_data_dir) for i in
                range(0, int(split_num)))

    def psi_compute(self,job_id_list,split_numlist,split_size1list,
                                      psi_store_data_dirlist,psi_listen_portlist,cpuPoolSizelist,index,bark_oprf_exe_dir):
        job_id = job_id_list
        split_num = split_numlist
        split_size1 = split_size1list
        psi_store_data_dir = psi_store_data_dirlist
        psi_listen_port = psi_listen_portlist
        cpuPoolSize = cpuPoolSizelist

        if split_num > 1:
            LOGGER.info('guest psi parallel compute start')
            self.psi_parallel_compute(split_num, split_size1, psi_store_data_dir, bark_oprf_exe_dir, psi_listen_port,
                                      cpuPoolSize, job_id)
            LOGGER.info('guest psi parallel compute finish')
            # 串行接收id
            for i in range(0, int(split_num)):

                flag = self.transfer_variable.intersectmd5id_list[i].get(idx=index)
                if not flag:
                    continue
                arr_id = self.transfer_variable.intersectmd5id_data_list[i].get(idx=index)
                arr_id = pd.DataFrame(arr_id, columns=['id'])

                arr_id_len = len(arr_id)
                if arr_id_len == 0:
                    continue
                arr_id = arr_id.applymap(lambda x: str(x))
                # 数据筛选
                path = ''.join([psi_store_data_dir, job_id, '_', 'data', '_', str(i), '.parquet'])
                guest_data1 = pd.read_parquet(path, engine='fastparquet')
                arr_id.set_index('id', inplace=True)
                temp = guest_data1.merge(arr_id, how='inner', left_on=['id'], right_index=True)
                path1 = ''.join([psi_store_data_dir, job_id, '_', 'inter', str(i), '.parquet'])
                temp.to_parquet(path1,
                                index=False, engine='fastparquet')
        elif split_num == 1:  # psi串行计算
            for i in range(0, int(split_num)):
                path = ''.join([psi_store_data_dir, job_id, '_', str(i), '.parquet'])
                if not os.path.exists(path):
                    continue

                command = ''.join([bark_oprf_exe_dir, " -r 0 ", path, " -ip ", '0.0.0.0:', str(psi_listen_port)])
                os.system(command)
                flag = self.transfer_variable.intersectmd5id_list[i].get(idx=index)
                if not flag :
                    break

                arr_id = self.transfer_variable.intersectmd5id_data_list[i].get(idx=index)
                arr_id = arr_id.applymap(lambda x: str(x))

                # 数据筛选
                path = ''.join([psi_store_data_dir, job_id, '_', 'data', '_', str(i), '.parquet'])
                guest_data1 = pd.read_parquet(path, engine='fastparquet')
                arr_id.set_index('id', inplace=True)
                temp = guest_data1.merge(arr_id, how='inner', left_on=['id'], right_index=True)

                path1 = ''.join([psi_store_data_dir, job_id, '_', 'inter', str(i), '.parquet'])
                temp.to_parquet(path1,
                                index=False, engine='fastparquet')

    # 多方psi并行计算
    def parallel_psi_compute(self,len_host_party,job_id_list,split_numlist,split_size1list,
                                      psi_store_data_dirlist,psi_listen_portlist,cpuPoolSizelist,bark_oprf_exe_dir):

        with Parallel(n_jobs=int(len_host_party),backend='multiprocessing') as p:
            lamdfun2P = partial(self.psi_compute)
            lld2 = p(
                delayed(lamdfun2P)(job_id_list[index:index + 1], split_numlist[index:index + 1],
                                   split_size1list[index:index + 1], psi_store_data_dirlist[index:index + 1],
                                   psi_listen_portlist[index:index + 1], cpuPoolSizelist[index:index+1],index,bark_oprf_exe_dir) for index in
                range(0, int(len_host_party)))

    def read_data(self,psi_store_data_dir,job_id,i):
        path = ''.join([psi_store_data_dir, job_id, '_', 'inter', str(i), '.parquet'])
        data = None
        if os.path.exists(path):
            data = pd.read_parquet(path, engine='fastparquet')
            LOGGER.info("data content----{}".format(data.shape))
        return data

    def parallel_read_data(self,psi_store_data_dir, job_id, split_num):
        data = None
        with Parallel(n_jobs=int(split_num),backend='multiprocessing') as p:
            lamdfun2P = partial(self.read_data)
            lld2 = p(
                delayed(lamdfun2P)(psi_store_data_dir,job_id, i) for i in
                range(0, int(split_num)))
            data = pd.concat(lld2, axis=0)
            del lld2
            gc.collect()
        return data

    def convert_table(self,guest_data):
        data_in = [(str(guest_data.loc[index, 'id']), guest_data.loc[index, 'id']) for index in guest_data.index]
        return data_in

    def parallel_convert_table(self,cpupoolsize,guest_data):
        c = len(guest_data)
        result = None
        sliceSize = max(ceil(c / (max(int(cpupoolsize), 1))), 1)
        iternum = max(ceil(c / sliceSize), 1)
        with Parallel(n_jobs=int(cpupoolsize), backend='multiprocessing') as p:
            lamdfun2P = partial(self.convert_table)
            lld2 = p(
                delayed(lamdfun2P)(guest_data.loc[(i * sliceSize):((i + 1) * sliceSize - 1), :]) for i in
                range(0, int(iternum)))
            for i in lld2:
                if result == None:
                    result = i
                else:
                    result = result+i

        return result

    # 并行对id进行加密
    def id_encrypt(self,split_num,cpuPoolSize,data_instance):
        sliceSize = max(ceil(self.base_rows / (max(int(cpuPoolSize),1))),1)
        iternum = max(ceil(self.base_rows / sliceSize),1)
        if split_num>1:
            with Parallel(n_jobs = int(cpuPoolSize),backend='multiprocessing') as p:
                lamdfun2P = partial(self.func)
                lld2 = p(
                    delayed(lamdfun2P)(data_instance.loc[(i * sliceSize):((i + 1) * sliceSize - 1), :], split_num) for i in
                    range(0,int(iternum)))
                LOGGER.info("starging----2------")
                data_instance = pd.concat(lld2,axis=0)

        else:
            data_instance["id"] = data_instance['id'].astype(str)
            data_instance.insert(0, 'md5', None)
            data_instance['md5'] = data_instance['id'].apply(lambda x: self.stringtomd5(x))
            data_instance['md5lastpos'] = 0

        return data_instance

    def psi_algorithms(self,psi_store_data_dir,bark_oprf_exe_dir,psi_listen_port,i,job_id):
        path = ''.join([psi_store_data_dir,job_id,'_',str(i),'.parquet'])
        if not os.path.exists(path):
            return
        command = ''.join([bark_oprf_exe_dir,' -r 0 ',path,' -ip ', '0.0.0.0',':',str(psi_listen_port+i)])
        os.system(command)

    def psi_algorithms2(self, psi_store_data_dir, psi_exe_dir, psi_pair_ip, psi_listen_port,
                        cpuPoolSize, j,job_id):
        path1 = ''.join([psi_store_data_dir,job_id,'_',str(j), '.parquet'])
        if not os.path.exists(path1):
            return
        command = ''.join([psi_exe_dir, " -r 1 ", path1, " -ip ", psi_pair_ip, ':', str(psi_listen_port + j)])
        os.system(command)


    def psi_parallel_compute2(self,split_num,split_size1,psi_store_data_dir,bark_oprf_exe_dir,psi_pair_ip,psi_listen_port,cpuPoolSize,job_id):
        for i in range(0,int(split_num/split_size1)):
            with Parallel(n_jobs=split_size1,backend='multiprocessing') as p:
                lamdfun2P = partial(self.psi_algorithms2)
                lld2 = p(delayed(lamdfun2P)(psi_store_data_dir,bark_oprf_exe_dir,psi_pair_ip,psi_listen_port,cpuPoolSize,j,job_id)
                         for j in range(split_size1*i,split_size1*(i+1)))

    def psi_parallel_compute(self,split_num,split_size1,psi_store_data_dir,bark_oprf_exe_dir,psi_listen_port,
                                      cpuPoolSize,job_id):
        for j in range(0,int(split_num/split_size1)):
            with Parallel(n_jobs=split_size1,backend='multiprocessing') as p:
                lamdfun2P = partial(self.psi_algorithms)
                lld2 = p(delayed(lamdfun2P)(psi_store_data_dir,bark_oprf_exe_dir,
                                            psi_listen_port,k,job_id)
                            for k in range(split_size1 * j,split_size1 * (j + 1)))
