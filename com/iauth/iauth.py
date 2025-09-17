import json
import struct
import time
import hashlib
import hmac
import random
import base64
import requests
import pickle
from Crypto.Cipher import AES
from base64 import b64decode, b64encode
from .cache import memorize


# 从IAuth获取 Token
# @memorize为开启Cache功能，单位为秒。建议用户开启; 非线程安全，如有需求请自行实现
# appId: 融合云 IAuth 后台申请的 ClientId
# appKey: Client 密钥
# scope: 访问服务的授权码，例如 30044
# sid: 需要访问的服务，例如 passport
# center: staging: http://staging.iauth.n.xiaomi.net
#         线上：https://iauth.pt.xiaomi.com
@memorize(600)
def get_token(appid, appkey, scope, sid, center):
    t = int(time.time())
    rd = random.getrandbits(64)
    nonce = base64.b64encode(struct.pack(">Q", rd) + struct.pack(">L", int(t / 60))).decode()
    salt = appkey
    params = "appId=%s&nonce=%s&scope=%s&sid=%s" % (appid, nonce, scope, sid)
    joind = "GET&/token/getToken&%s&%s" % (params, salt)
    sign = base64.b64encode(hashlib.sha1(joind.encode()).digest())

    url = "%s/token/getToken" % center

    payload = {'appId': appid, 'nonce': nonce, 'scope': scope, 'sid': sid, '_sign': sign}
    ret = requests.get(url, params=payload)
    return ret.text


def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes



BLOCK_SIZE = AES.block_size
# 不足BLOCK_SIZE的补位(s可能是含中文，而中文字符utf-8编码占3个位置,gbk是2，所以需要以len(s.encode())，而不是len(s)计算补码)
pad = lambda s: s + (BLOCK_SIZE - len(s.encode()) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s.encode()) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def encrypt(text):
    key = 'serviceKey'  # 密钥
    iv = '0102030405060708'  # 偏移量
    text = pad(text).encode()  # 包pycryptodome 的加密函数不接受str
    iv.encode()
    cipher = AES.new(b64decode(key), AES.MODE_CBC, iv.encode())
    encrypted_text = cipher.encrypt(text)
    return b64encode(encrypted_text).decode('ISO-8859-1')


def decrypt(text):
    key = 'serviceKey'  # 密钥
    iv = '0102030405060708'  # 偏移量
    encrypted_text = b64decode(text)
    cipher = AES.new(b64decode(key), AES.MODE_CBC, iv.encode())
    decrypted_text = cipher.decrypt(encrypted_text)
    return unpad(decrypted_text).decode('ISO-8859-1')

# service端从iauth获取token，用来解密客户端传入的fullToken
def decryptToken(tokenKey, fullToken):
    splitArr = fullToken.split('&')
    version = splitArr[0]
    sid = splitArr[1]
    compositeToken = splitArr[2]
    sign = splitArr[3]

    strArr = compositeToken.split(':')
    ivString = strArr[1]
    missing_padding = 4 - len(ivString) % 4
    if missing_padding:
        ivString += '=' * missing_padding

    print(ivString)
    iss = base64.urlsafe_b64decode(ivString)

    encryptedToken = strArr[2]
    print(encryptedToken)
    encrypted_text = b64decode(encryptedToken)
    cipher = AES.new(b64decode(tokenKey), AES.MODE_CBC, iss)
    decrypted_text = cipher.decrypt(encrypted_text)
    return unpad(decrypted_text).decode('ISO-8859-1')



# 加密方法
def encrypt_oracle(key):
    # 秘钥
    # 待加密文本
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_CBC)
    # 先进行aes加密
    encrypt_aes = aes.encrypt(add_to_16(key))
    # 用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    print(encrypted_text)
    return encrypted_text

# 从 IAuth获取TokenKey
# sid： 服务端sid
# serviceKey： 服务端身份密钥
# aesKey: 经salt加密后的aesKey
# center: staging: http://staging.iauth.n.xiaomi.net
#         线上：https://iauth.pt.xiaomi.com
def get_token_key(sid, serviceKey, aesKey, center):
    t = int(time.time())
    rd = random.getrandbits(64)
    nonce = base64.b64encode(struct.pack(">Q", rd) + struct.pack(">L", int(t / 60))).decode()
    salt = serviceKey

    params = "key=%s&nonce=%s&sid=%s" % (aesKey, nonce, sid)

    joind = "GET&/service/V3/key&%s" % (params)
    sign = base64.b64encode(hmac.new(salt.encode(), joind.encode(), hashlib.sha1).digest()).decode()

    url = "%s/service/V3/key" % center

    # 参数中的key 为aes加密后的salt
    payload = {'sid': sid, 'key': aesKey, 'nonce': nonce, '_sign': sign}
    ret = requests.get(url, params=payload)
    return ret.text


# 从Service端获取资源
# appid: Client端id
# token: 从IAuth获取的Token
# Url: Service端的服务地址，这里需要咨询你访问的服务
def get_resource(appid, token, url):
    # 需要附带的参数
    payload = {'appId': appid, 'token': token}
    body = {
        "device": "thor",
        "token": "60ad43a3de3754614899e27bd30dbb47"
    }
    ret = requests.get(url, params=payload, data=json.dumps(body))
    return ret.text