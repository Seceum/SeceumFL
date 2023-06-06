from federatedml.statistic.intersect.bark_oprf_intersect.bark_oprf_intersect_base import BaRK_OPRF_Intersection
from federatedml.util import consts, LOGGER
from federatedml.util.data_compress_decompress import zlibcompress,zlibdecompress_dataframe
from math import ceil,sqrt
import multiprocessing
import os
import pandas as pd
import gc
from pipeline.utils.tools import load_job_config
import uuid
import time
from pathlib import Path
from fate_arch.common import file_utils, conf_utils
from fate_arch.common.conf_utils import SERVICE_CONF
from fate_arch.common.conf_utils import get_base_config
import subprocess

class BaRK_OPRF_IntersectHost(BaRK_OPRF_Intersection):
    def __init__(self):
        super().__init__()
        self.role = consts.HOST
        self.job_id = ''.join(str(uuid.uuid4()).split('-'))

    def bark_oprf_calculation_process(self,data_instance):
        LOGGER.info("host bark oprf content {}".format(get_base_config("bark_oprf")))
        psi_pair_ip = get_base_config("bark_oprf")["psi_pair_ip"]
        LOGGER.info('psi pair ip---{}'.format(psi_pair_ip))
        self.transfer_variable.job_id.remote(self.job_id,role=consts.GUEST,idx=0)
        self.base_rows = data_instance.count()
        self.transfer_variable.host_data_num.remote(self.base_rows,role=consts.GUEST,idx=0)
        guest_data_num = self.transfer_variable.guest_data_num.get(idx=0)
        LOGGER.info('receive guest data num----{}'.format(guest_data_num))
        tempmax = max(self.base_rows,guest_data_num)
        stopvalue = self.cal_stopvalue(tempmax)
        split_size = self.getchildren(tempmax,stopvalue)

        # 分片数量
        split_num = tempmax / split_size
        # 样本数量为质数
        if split_num == tempmax:
            split_num = int(ceil(tempmax / stopvalue))
            if split_num %2 == 1:
                split_num = split_num + 1

        cpuPoolSize = multiprocessing.cpu_count()
        data_instance = self.data_format_convert_to_dataframe(data_instance)
        # 对id进行加密
        if self.need_encrypt:
            data_instance = self.id_encrypt(split_num,split_num,data_instance)

        #存储结果的路径
        psi_store_data_dir = '/data/psi/data/'
        if os.path.isdir(psi_store_data_dir):
            pass
        else:
            os.makedirs(psi_store_data_dir)

        psi_listen_port = self.transfer_variable.psi_listen_port.get(idx=0)
        LOGGER.info("psi listen port----{}".format(psi_listen_port))
        psi_exe_dir = '/opt/BaRK-OPRF/Release/bOPRFmain.exe'
        #不需要分片，两边的数据量一样多
        if split_num == 1:
            #host方数据比guest方数据少
            if self.base_rows < guest_data_num:
                t = ceil(guest_data_num / self.base_rows)
                t = ceil(sqrt(t))
                for i in range(int(t)+1):
                    data_instance = pd.concat([data_instance,data_instance],axis=0)
                data_instance.reset_index(inplace=True,drop=True)
                data_instance = data_instance.loc[0:(guest_data_num-1),:]
                # add by tjx 202242
                mask = pd.DataFrame(data_instance['md5']).apply(pd.Series.duplicated, axis=0)
                data_instance['md5'] = pd.DataFrame(data_instance['md5']).mask(mask, None)
                data_instance['md5'] = data_instance['md5'].apply(
                    lambda x: ''.join(str(uuid.uuid4()).split('-')) if x == None else x)

            temppath = ''.join([psi_store_data_dir, self.job_id,'_', str(0), '.parquet'])
            pd.DataFrame(data_instance['md5'], columns=['md5']).to_parquet(temppath, index=False, engine='fastparquet')
            LOGGER.info('host save md5 data')
            path = ''.join([psi_store_data_dir, self.job_id,'_', 'data', '_', str(0), '.parquet'])
            data_instance.to_parquet(path, index=False, engine='fastparquet')
            LOGGER.info('host save origin data')

        else:
            # 需要分片
            f = 0
            #f=0时候效率比f=1高
            # host并行分片 ,通信不行
            if f == 1:
                LOGGER.info('host split data parallel')
                [self.host_split_data(data_instance.loc[(data_instance['md5lastpos']==i),:],self.job_id,i,psi_store_data_dir)
                 for i in range(0,split_num)]

            # host串行分片
            if f == 0:
                for i in range(0,int(split_num)):
                    try:
                        data = data_instance.loc[(data_instance['md5lastpos']==i),:]
                    except:
                        continue
                    datalen = len(data)
                    self.transfer_variable.host_data_num_list[i].remote(datalen,role=consts.GUEST,idx=0)
                    guest_data_num = self.transfer_variable.guest_data_num_list[i].get(idx=0)
                    #当其中一方没有数据
                    if datalen == 0 or guest_data_num == 0:
                        continue
                    if datalen < guest_data_num:
                        t = ceil(guest_data_num / datalen)
                        t = ceil(sqrt(t))
                        for j in range(int(t)+1):
                            data = pd.concat([data,data],axis=0)
                        data.reset_index(inplace=True,drop=True)
                        data = data.loc[0:(guest_data_num - 1), :]
                        # add by tjx 202242
                        mask = pd.DataFrame(data['md5']).apply(pd.Series.duplicated, axis=0)
                        data['md5'] = pd.DataFrame(data['md5']).mask(mask, None)
                        data['md5'] = data['md5'].apply(
                            lambda x:  ''.join(str(uuid.uuid4()).split('-')) if x == None else x)

                    path = ''.join([psi_store_data_dir, self.job_id, '_', str(i), '.parquet'])
                    pd.DataFrame(data['md5'], columns=['md5']).to_parquet(path, index=False, engine='fastparquet')
                    path = ''.join([psi_store_data_dir, self.job_id,'_','data', '_', str(i), '.parquet'])
                    if 'flag' in data.columns:
                        del data['flag']
                    if 'md5lastpos' in data.columns:
                        del data['md5lastpos']
                    data.to_parquet(path, index=False, engine='fastparquet')
                    LOGGER.info('host save split data')

        # 计算psi split_size1 psi并行数量，最大为split_num一半
        if split_num >= multiprocessing.cpu_count() and tempmax > 60000000:
            split_size1 = self.getchildren(split_num,split_num/2)
        else:
            split_size1 = int(split_num)

        # psi并行计算
        if split_num > 1:
            LOGGER.info('psi parallel compute start')
            self.psi_parallel_compute2(split_num,split_size1,psi_store_data_dir,psi_exe_dir,psi_pair_ip,psi_listen_port,cpuPoolSize,self.job_id)
            LOGGER.info('psi parallel compute finish')
            for j in range(0,int(split_num)):
                path = ''.join([psi_store_data_dir, self.job_id,'_',str(j), '.txt'])
                if os.path.exists(path):
                    try:
                        if os.path.getsize(path)==0:
                            self.transfer_variable.intersectmd5id_list[j].remote(False, role=consts.GUEST, idx=0)
                            continue

                        data = pd.read_csv(path, header=None)
                        data.columns = ['md5id']
                        if len(data) == 0:
                            self.transfer_variable.intersectmd5id_list[j].remote(False,role=consts.GUEST,idx=0)
                            continue
                        else:
                            self.transfer_variable.intersectmd5id_list[j].remote(True,role=consts.GUEST,idx=0)
                    except:
                        self.transfer_variable.intersectmd5id_list[j].remote(False, role=consts.GUEST, idx=0)
                        continue
                else:
                    self.transfer_variable.intersectmd5id_list[j].remote(False, role=consts.GUEST, idx=0)
                    continue

                path = ''.join([psi_store_data_dir, self.job_id,'_','data', '_', str(j), '.parquet'])
                host_data1 = pd.read_parquet(path, engine='fastparquet')
                data.set_index('md5id', inplace=True)
                temp = host_data1.merge(data, how='inner', left_on=['md5'], right_index=True)
                # 串行发送数据
                self.transfer_variable.intersectmd5id_data_list[j].remote(zlibcompress(pd.DataFrame(temp['id'],columns=['id'])),role=consts.GUEST,idx=0)


        elif split_num == 1:#psi串行计算
            for j in range(0,int(split_num)):
                path1 = ''.join([psi_store_data_dir, self.job_id,'_',str(j), '.parquet'])
                if not os.path.exists(path1):
                    continue

                command = ''.join([psi_exe_dir, " -r 1 ", path1, " -ip ", psi_pair_ip + ':', str(psi_listen_port)])
                LOGGER.info("host command----{}".format(command))
                LOGGER.info("path--env---{}".format(os.getenv("PATH")))
                try:
                    os.system(command)
                except Exception as e:
                    LOGGER.info(" error---------- {}".format(e))
                path = ''.join([psi_store_data_dir, self.job_id, '_', str(j), '.txt'])
                LOGGER.info("path---------{}".format(path))
                time.sleep(10)
                if os.path.exists(path):
                    try:
                        if os.path.getsize(path)==0:
                            self.transfer_variable.intersectmd5id_list[j].remote(False, role=consts.GUEST, idx=0)
                            break
                        data = pd.read_csv(path,header=None)
                        data.columns = ['md5id']
                        if len(data) == 0:
                            self.transfer_variable.intersectmd5id_list[j].remote(False,role=consts.GUEST,idx=0)
                            continue
                        else:
                            self.transfer_variable.intersectmd5id_list[j].remote(True,role=consts.GUEST,idx=0)
                    except:
                        self.transfer_variable.intersectmd5id_list[j].remote(False, role=consts.GUEST, idx=0)
                        break
                else:
                    self.transfer_variable.intersectmd5id_list[j].remote(False, role=consts.GUEST, idx=0)
                    break

                # 发送数量
                path = ''.join([psi_store_data_dir, self.job_id, '_', 'data', '_', str(j), '.parquet'])
                host_data1 = pd.read_parquet(path, engine='fastparquet')
                data.set_index('md5id', inplace=True)
                temp = host_data1.merge(data, how='inner', left_on=['md5'], right_index=True)
                self.transfer_variable.intersectmd5id_data_list[j].remote(zlibcompress(pd.DataFrame(temp["id"],columns=['id'])), role=consts.GUEST, idx=0)

        #接收guest方最终公共id
        host_data = None
        if self.sync_intersect_ids:
            host_data = self.transfer_variable.intersect_ids.get(idx=0)
        return host_data

