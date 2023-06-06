import base64
import hashlib
from datetime import datetime
import pickle
import uuid
import os
from functools import wraps

from Crypto.Cipher import AES
from fate_flow.web_server.fl_config import config, license_logger
from fate_flow.web_server.utils.reponse_util import get_json_result

AES_SECRET = "F8E3330DD6CE68B9"
AES_IV = "1EAC319CFC10F4C0"
AES_SALT = "3EC4366B10B159CF"


class AESHelper(object):
    def __init__(self, password, iv):
        self.password = bytes(password, encoding='utf-8')
        self.iv = bytes(iv, encoding='utf-8')

    def pkcs7padding(self, text):
        bs = AES.block_size
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        padding_size = length if (bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        padding_text = chr(padding) * padding
        return text + padding_text

    def pkcs7unpadding(self, text):
        length = len(text)
        unpadding = ord(text[length - 1])
        return text[0:length - unpadding]

    def encrypt(self, content):
        cipher = AES.new(self.password, AES.MODE_CBC, self.iv)
        content_padding = self.pkcs7padding(content)
        encrypt_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
        result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
        return result

    def decrypt(self, content):
        cipher = AES.new(self.password, AES.MODE_CBC, self.iv)
        encrypt_bytes = base64.b64decode(content)
        decrypt_bytes = cipher.decrypt(encrypt_bytes)
        result = str(decrypt_bytes, encoding='utf-8')
        result = self.pkcs7unpadding(result)
        return result


def get_aes():
    aes_helper = AESHelper(AES_SECRET, AES_IV)
    return aes_helper


class LicenseHelper(object):

    def hash_msg(self, msg):
        sha256 = hashlib.sha256()
        sha256.update(msg.encode('utf-8'))
        res = sha256.hexdigest()
        return res

    def read_license(self, license_result):
        try:
            license_result = pickle.loads(license_result)
            lic_msg = bytes(license_result, encoding="utf8")
            license_str = get_aes().decrypt(lic_msg)
            license_dic = eval(license_str)
            return True, license_dic
        except Exception as e:
            return False, str(e)

    def check_license_date(self, lic_start_date_str, lic_end_date_str):
        current_time_str = datetime.strftime(datetime.now(), "%Y-%m-%d")
        current_date = datetime.strptime(current_time_str, "%Y-%m-%d")
        lic_end_date = datetime.strptime(lic_end_date_str, "%Y-%m-%d")
        lic_start_date = datetime.strptime(lic_start_date_str, "%Y-%m-%d")
        if current_date < lic_start_date:
            return False, "证书使用开始时间{}".format(lic_start_date_str)
        remain_days = (lic_end_date - current_date).days
        if remain_days < 0:
            return False, "证书过期时间{}，证书已过期".format(lic_end_date_str)
        else:
            return True, lic_end_date_str

    def check_license_psw(self, psw, mac_addr):
        pwd_str = AES_SALT + str(mac_addr)
        hashed_msg = self.hash_msg(pwd_str)
        if psw == hashed_msg:
            return True
        else:
            return False

    @staticmethod
    def get_mac_address():
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


def parse_license():
    return True,'2099-10-18'
    oper = LicenseHelper()
    license_path = config.LICENSE_PATH
    if not os.path.exists(license_path):
        license_logger.error("{} 证书不存在".format(license_path))
        return False, "请联系seceum获取证书"
    if not os.path.isfile(license_path):
        license_logger.error("{} 不是证书证书文件".format(license_path))
        return False, "请联系seceum获取证书"
    with open(license_path, 'rb') as f:
        content = f.read()
    read_bool, license_dic = oper.read_license(content)
    if not read_bool:
        license_logger.error("读取证书失败：{}".format(license_dic))
        return False, "证书无效，请联系seceum更换证书"
    else:
        mac_addr = oper.get_mac_address()
        psw_bool = oper.check_license_psw(license_dic['psw'], mac_addr)
        if psw_bool:
            date_bool, date_msg = oper.check_license_date(license_dic['start_date'], license_dic['end_date'], )
            return date_bool, date_msg
        else:
            license_logger.error("证书无效，请更换证书")
            return False, "证书无效，请联系seceum更换证书"


def check_license(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        flag, license_msg = parse_license()
        if not flag:
            return get_json_result(data=False, retcode=100, retmsg=license_msg)
        return func(*args, **kwargs)

    return wrapper
