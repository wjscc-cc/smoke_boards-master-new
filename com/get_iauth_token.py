import configparser
import json
import os.path
from com.iauth.iauth import get_token

cp = configparser.RawConfigParser()
file = os.path.join(os.path.dirname(__file__), 'request.ini')
cp.read(file)

iauth_appid = cp.get('iauth', 'iauth_appid')
iauth_apikey = cp.get('iauth', 'iauth_apikey')
iauth_pd_sid = cp.get('pd', 'iauth_pd_sid')
iauth_pd_scope = cp.get('pd', 'iauth_pd_scope')
iauth_center = cp.get('iauth', 'iauth_center')
iauth_center_test = cp.get('iauth', 'iauth_center_test')


token_iauth_filepath = os.path.join(os.path.dirname(__file__), 'cookies', 'token_iauth')


def get_token_iauth_old():
    if os.path.isfile(token_iauth_filepath):
        with open(token_iauth_filepath) as _F:
            return _F.read()
    else:
        return get_token_iauth_new()


def get_token_iauth_new():
    r = get_token(iauth_appid, iauth_apikey, iauth_pd_scope, iauth_pd_sid, iauth_center)
    token_ret = json.loads(r)
    if token_ret.get('data') and token_ret.get('data').get('token'):
        token_auth = token_ret['data']['token']
        with open(token_iauth_filepath, 'w') as _F:
            _F.write(token_auth)
        print('保存了新iauth=[{}]'.format(token_auth))
        return token_auth
    else:
        print('iauth_token 获取失败')
        print(token_ret)
        return None


if __name__ == '__main__':
    print(get_token_iauth_new())