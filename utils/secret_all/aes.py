import base64
import binascii

from Crypto.Cipher import AES
from conf.settings import backend_settings

pad = lambda s: (s + (16 - len(s) % 16) * chr(16 - len(s) % 16))  # -- 填充函数


class Encryption:
    """手机号加解密"""

    def __init__(self, data):
        self.data = data
        self.__key = backend_settings.aes_key

    def encrypt(self):
        """加密"""
        pad = lambda s: (s + (16 - len(s) % 16) * chr(16 - len(s) % 16))  # 填充函数，不够的补位数
        raw = pad(str(self.data))  # 拿到补位后的数据
        cipher = AES.new(self.__key.encode(), AES.MODE_ECB)  # 加密模式 选择用ECB加密，是一个对象
        encrypted_text = cipher.encrypt(bytes(raw, encoding="utf8"))  # 开始加密，编码格式是utf8
        encrypted_text_base64 = base64.b64encode(
            encrypted_text
        )  # 进行编码为二进制，结果是二进制  b'xxxxxx'
        result = (
            binascii.hexlify(encrypted_text_base64).decode("utf8").upper().strip()
        )  # 进行编码转换，表示为二进制数据的十六进制
        return result

    def decrypt(self):
        """解密"""
        data = binascii.unhexlify(self.data)  # 十六进制进行解码转换
        # print(data)  # b'xxxxx'
        encode_bytes = base64.decodebytes(data)  # 可以将二进制转化为正常形式
        cipher = AES.new(self.__key.encode("utf8"), AES.MODE_ECB)  # 解密模式，是一个对象
        text_decrypted = cipher.decrypt(encode_bytes)  # 开始解密
        unpad = lambda s: s[0 : -s[-1]]  # 逆填充函数，去掉空格
        text_decrypted = unpad(text_decrypted)  # 拿到去掉补位后的数据
        text_decrypted = text_decrypted.decode("utf8")  # 解码字符串以utf8
        return text_decrypted


def aes_encrypt(data):
    return Encryption(data=data).encrypt()


def aes_decrypt(data):
    return Encryption(data=data).decrypt()
