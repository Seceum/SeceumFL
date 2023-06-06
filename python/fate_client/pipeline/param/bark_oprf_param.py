
from federatedml.param.base_param import BaseParam
from federatedml.util import consts, LOGGER

class BaRK_OPRFParam(BaseParam):
    """
    specify parameters for BaRK OPRF intersect method
    add by tjx 20220222
    Parameters
    -------------
    encrypt_method:str
        the encrypt method only support md5,in order to make all id length same,all id need to encrypt by md5
        default 'md5'

    need_encrypt:bool
        if origin id have been encrypted  the need_encrypt param is False
        else origin id need to be encrypt the need_encrypt param is True
        default need_encrypt param is True
    """

    def __init__(self,encrypt_method='md5',need_encrypt=True):
        super().__init__()
        self.encrypt_method = encrypt_method
        self.need_encrypt = need_encrypt

    def check(self):
        descr = "bark oprf param's"
        # self.encrypt_method = self.check_and_change_lower(self.encrypt_method,['md5'],f"{descr}encrypt_method")

        self.check_boolean(self.need_encrypt,f"{descr}need_encrypt")

        LOGGER.debug('finish bark oprf param check!')
        return True

