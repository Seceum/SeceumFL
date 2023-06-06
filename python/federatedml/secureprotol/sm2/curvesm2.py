
from federatedml.secureprotol.sm2.sm2_util import *
from federatedml.secureprotol.sm2.sm2 import *

class CurveSM2(object):

    def __init__(self):
        self.sm2 = SM2(genkeypair=True)
        self.d,P = self.sm2.gen_keypair()


    def get_private_key(self) -> bytes:
        return self.d

    def encrypt(self, m: bytes) :
        """encrypt message.
        This contains flowing steps:
        1. Perform hashing to the group using the Elligator2 map to
            generate a Montgomery Point `A` in curve25519.
            (See https://tools.ietf.org/html/draft-irtf-cfrg-hash-to-curve-10#section-6.7.1)
        2. Perform scalar multipication `A * Scalar(secret)` to generate Montgomery Point `B`
        3. return `B` represents by 32 bytes value
        Args:
            m (bytes): message to encrypt

        Returns:
            bytes: encryptd message in 32-length bytes
        """
        point_temp = bytes_to_point(to_byte(m, 31))
        Q = self.sm2.multiply(self.d,point_temp)
        return Q

    def diffie_hellman(self, pub: bytes) -> bytes:
        """generate diffie_hellman like sharedsecret.

        Args:
            pub (bytes): encryted message in 32-length bytes.

        Returns:
            bytes: sharedsecret in 32-length bytes
        """
        Q = self.sm2.multiply(self.d,pub)
        return Q

