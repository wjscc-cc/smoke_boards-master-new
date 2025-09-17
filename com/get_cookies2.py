# -- coding: utf-8 --
import os
import sys
import json
import base64
import hashlib

from loguru import logger
import requests
import requests.utils
# from Crypto.Cipher import AES  # pip install pycrypto
from Crypto.Cipher import AES  # pip install pycrypto

# appid = '9c98216d'
# appkey = '8c5942a7c1ce445e'
# username = 'mi-specialtest'
# password = 'Zhejiang1228@@'

appid = '661e9896'
appkey = '1874fbab83ad4b1d'
username = 'xts-robot'
password = 'Xm4Lg07B91G6'
#
"""appid = 'bda75a5e'
appkey = '03c8d5ee944847f7'
username = 'smoke-robot'
password = 'XmwK00X91Bu2'
"""


if getattr(sys, 'frozen', None):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(__file__)
COOKIES_DIR = os.path.join(os.path.abspath(BASE_PATH), 'cookies')


def _gen_gson_safe_chars_map():
    '''
    static {
        REPLACEMENT_CHARS = new String[128];
        for (int i = 0; i <= 0x1f; i++) {
            REPLACEMENT_CHARS[i] = String.format("\\u%04x", (int) i);
        }
        REPLACEMENT_CHARS['"'] = "\\\"";
        REPLACEMENT_CHARS['\\'] = "\\\\";
        REPLACEMENT_CHARS['\t'] = "\\t";
        REPLACEMENT_CHARS['\b'] = "\\b";
        REPLACEMENT_CHARS['\n'] = "\\n";
        REPLACEMENT_CHARS['\r'] = "\\r";
        REPLACEMENT_CHARS['\f'] = "\\f";
        HTML_SAFE_REPLACEMENT_CHARS = REPLACEMENT_CHARS.clone();
        HTML_SAFE_REPLACEMENT_CHARS['<'] = "\\u003c";
        HTML_SAFE_REPLACEMENT_CHARS['>'] = "\\u003e";
        HTML_SAFE_REPLACEMENT_CHARS['&'] = "\\u0026";
        HTML_SAFE_REPLACEMENT_CHARS['='] = "\\u003d";
        HTML_SAFE_REPLACEMENT_CHARS['\''] = "\\u0027";
    }
    '''

    # below characters in python3 will be automatic converted to safe characters
    # see json/encoder.py:21
    # + (0x0000...0x0001f, '\\u{:04x}')
    # + ('"', '\\\"'),
    # + ('\\', '\\\\'),
    # + ('\t', '\\t'),
    # + ('\b', '\\b'),
    # + ('\n', '\\n'),
    # + ('\r', '\\r'),
    # + ('\f', '\\f'),
    return (('<', "\\u003c"), ('>', "\\u003e"), ('&', "\\u0026"),
            ('=', "\\u003d"), ('\'', "\\u0027"))


_gson_safe_chars_map = _gen_gson_safe_chars_map()


def json_to_string(data):
    '''
    一个兼容gson的字符串转换
    '''
    string = json.dumps(data, separators=(',', ':'))
    for (src, dest) in _gson_safe_chars_map:
        string = string.replace(src, dest)
    return string


def x5_sign(appid, appkey, body):
    '''
    计算x5头部的sign值
    '''
    if not isinstance(body, str):
        body = json_to_string(body)

    concated = appid + body + appkey
    res = hashlib.md5(concated.encode(encoding='utf-8'))
    res = res.hexdigest()
    res = res.upper()
    return res


def x5_data(header, body):
    '''
    生成x5协议POST的载荷
    '''
    data = {
        'header': header,
        'body': body,
    }

    assert header.get('sign', None), "`sign` cannot be empty in x5 header"

    data = json_to_string(data)
    data = base64.b64encode(data.encode('utf-8'))
    data = data.decode('utf-8')
    return {'data': data}


def encrypt(appkey, content):
    '''
    auto login的密码加密
    '''

    # PKCS5Padding
    def add_paddings(block_size):
        padding = block_size - len(content) % block_size
        return content + chr(padding) * padding

    # 注意: 由于不同版本pycrypto导致的兼容性问题，以下几个fixme可能解决你遇到的问题

    # FIXME: 传`appkey.encode('utf-8')`替换传递`appkey`
    try:
        chipher = AES.new(appkey, AES.MODE_ECB)
    except:
        chipher = AES.new(appkey.encode('utf-8'), AES.MODE_ECB)

    # FIXME： 传`16`替换传递`chipher.block_size`
    try:
        content = add_paddings(chipher.block_size)
    except:
        content = add_paddings(16)

    # FIXME: 传 `content.encode('utf-8')`替换传递`content`
    try:
        res = chipher.encrypt(content)
    except:
        res = chipher.encrypt(content.encode('utf-8'))

    res = base64.b64encode(res)
    res = res.decode('utf-8')
    return res


class CASSession(requests.Session):
    '''
        实现了自动登录的session封装
    '''

    CAS_URL = 'https://cas.mioffice.cn/login'

    CAS_AUTO_LOGIN_URL = 'https://cas.mioffice.cn/v2/api/auto/login'

    # 以下几个变量，可以通过一个backend去存储，来扩展。
    # 为了演示，这里就简单地使用了变量。

    APP_ID = ''
    APP_KEY = ''
    USERNAME = ''
    PASSWORD = ''

    @classmethod
    def cas_config(cls, *, app_id, app_key, username, password):
        cls.APP_ID = app_id
        cls.APP_KEY = app_key
        cls.USERNAME = username
        cls.PASSWORD = encrypt(app_key, password)

    @classmethod
    def cas_data(cls, service):
        body = {
            'username': cls.USERNAME,
            'password': cls.PASSWORD,
            'service': service
        }
        header = {
            'appid': cls.APP_ID,
            'sign': x5_sign(cls.APP_ID, cls.APP_KEY, body)
        }
        return x5_data(header, body)

    def cas_autologin(self, service):
        '''
            调用cas的auto login接口。
            service为需要访问的url服务。
            如果成功，返回重定向的url；
            否则，返回None。
        '''
        data = self.cas_data(service)
        res = self.post(self.CAS_AUTO_LOGIN_URL, data, allow_redirects=False)
        res = json.loads(res.content.decode('utf-8'))
        status = res.get('status', -1)
        if status != 0:
            print(f'auto login failed with {status} {res.get("message", "")}')
            return None
        return res.get('data', {}).get('redirect_to', None)

    def get_redirect_target(self, resp):
        '''
            重载该方法是为了在重定向到cas登录页面的时候，调用cas的auto login获取自动的重定向的url。
        '''
        import urllib.parse as urlparse

        if resp.is_redirect:
            location = resp.headers['location']

            if location.startswith(self.CAS_URL):
                query = urlparse.urlparse(location).query
                url = urlparse.parse_qs(query).get('service', '')

                if not isinstance(url, str):
                    url = url[0]

                return self.cas_autologin(url)
            else:
                return super().get_redirect_target(resp)
        return None


def update_cookies(url):
    # url = 'https://corgi.pt.miui.com/'
    url_name = url.strip('https://').strip('http://').split('.')[0]

    session = CASSession()

    session.cas_config(
        app_id=appid,
        app_key=appkey,
        username=username,
        password=password,
    )

    resp = session.get(url)
    if resp.status_code != 200:
        print('login failed.')
        txt = json.loads(resp.text)
        print('_+_+_+'*20)
        print('txt.get()=[{}]'.format(txt.get('login_url')))
        if txt.get('login_url'):
            url_login = 'https://postci.pt.xiaomi.com'+txt.get('login_url')
            print("url_login=", url_login)
            resp = session.get(url_login)
            print(resp.status_code)
            print(resp.text)
            if resp.status_code != 200:
                print('login failed2.')
        else:
            exit(-1)
    resp = session.get(url)
    if resp.status_code != 200:
        print('login failed.')
        txt = json.loads(resp.text)
        print('_+_+_+'*20)
        print('txt.get()=[{}]'.format(txt.get('login_url')))
        if txt.get('login_url'):
            url_login = 'https://postci.pt.xiaomi.com'+txt.get('login_url')
            print("url_login=", url_login)
            resp = session.get(url_login)
            print(resp.status_code)
            print(resp.text)
            if resp.status_code != 200:
                print('login failed2.')
        else:
            exit(-1)

    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    logger.debug('update cookies: {}'.format(cookies))
    with open(os.path.join(COOKIES_DIR, url_name+'_cookie.txt'), 'w') as f:
        f.write(json.dumps(cookies))
    return cookies


def get_cookie_from_txt(url):
    """
    get cookies form txt file, is cookies out of date, update it
    :return: dict
    """
    # url = 'https://corgi.pt.miui.com/api/device/item/list'
    url_name = url.strip('https://').strip('http://').split('.')[0]
    cookie_file = os.path.join(COOKIES_DIR, url_name + '_cookie.txt')
    if not os.path.isfile(cookie_file):
        cookies = update_cookies(url)
    else:
        with open(cookie_file, 'r') as f:
            cookies = json.loads(f.read())

    print(url)
    res = requests.get(url=url, cookies=cookies)
    print(res.text)
    if '内网统一认证' in res.text or 'login_url' in str(res.text):
        logger.info('cookies过期，正在重新获取cookies')
        logger.info(url_name)
        cookies = update_cookies(url)
        logger.info('cookie 获取完成')
    return cookies


def request_auto(url):
    # 获取cookie
    if 'http' not in str(url):
        print('请求的链接异常  url=[{}]'.format(url))
        return False
    url_name = url.strip('https://').strip('http://').split('.')[0]
    cookie_file = os.path.join(COOKIES_DIR, url_name + '_cookie.txt')
    # print(cookie_file)
    if not os.path.isfile(cookie_file):
        cookies = update_cookies(url)
    else:
        with open(cookie_file, 'r') as f:
            cookies = json.loads(f.read())
    # 使用cookie请求一次
    # s = requests.session()
    # s.headers['User - Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    res = requests.get(url=url, cookies=cookies)
    # 如果cookie有问题再更新
    if '内网统一认证' in res.text or 'login_url' in str(res.text):
        logger.info('cookies过期，正在重新获取cookies')
        logger.info(url_name)
        cookies = update_cookies(url)
        # 更新cookie后再请求一次
        res = requests.get(url=url, cookies=cookies)
    return res
def request_result(url):
    # 获取cookie
    if 'http' not in str(url):
        print('请求的链接异常  url=[{}]'.format(url))
        return False
    url_name = url.strip('https://').strip('http://').split('.')[0]
    cookie_file = os.path.join(COOKIES_DIR, url_name + '_cookie.txt')
    if not os.path.isfile(cookie_file):
        cookies = update_cookies(url)
    else:
        with open(cookie_file, 'r') as f:
            cookies = json.loads(f.read())
    # 使用cookie请求一次
    # s = requests.session()
    # s.headers['User - Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    res = requests.get(url=url, cookies=cookies)
    # 如果cookie有问题再更新
    if '内网统一认证' in res.text or 'login_url' in str(res.text):
        logger.info('cookies过期，正在重新获取cookies')
        logger.info(url_name)
        cookies = update_cookies(url)
        # 更新cookie后再请求一次
        res = requests.get(url=url, cookies=cookies)
    return res

if __name__ == '__main__':
    update_cookies("")
