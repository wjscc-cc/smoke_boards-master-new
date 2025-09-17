import json
import os.path
import time

import requests
import configparser

from com import get_iauth_token

cp = configparser.RawConfigParser()
file = os.path.join(os.path.dirname(__file__), 'request.ini')
cp.read(file)

iauth_appid = cp.get('iauth', 'iauth_appid')
pd_center = cp.get('pd', 'pd_center')
# pd_center_test = cp.get('pd', 'pd_center_test')
token_pd = cp.get('pd', 'pd_token')

FILE_PATH = os.path.dirname(__file__)
last_time_log_filepath = os.path.join(FILE_PATH, 'last_time_log')


def requests_pd_auto(path, body_dict):
    """
    res = requests_pd(appid, token_auth, body, url + path)
    payload = {'appId': appid, 'token': token_iauth}
    ret = requests.get(pd_url, params=payload, data=json.dumps(body))
    """
    token_iauth = get_iauth_token.get_token_iauth_old()
    if 'http' in path:
        url = path
    else:
        url = pd_center + path
    body_dict['token'] = token_pd

    body = json.dumps(body_dict)
    payload = {'appId': iauth_appid, 'token': token_iauth}

    # need_sleep_time = get_need_sleep_time()
    # time.sleep(need_sleep_time)
    print(payload)
    print(body)
    res = requests.get(url, params=json.dumps(payload), data=body)
    if '失效' in res.text or 'MOCK_RESPONSE' in res.text or '"code":500' in res.text:
        print('请求错误, 实际返回结果为')
        print(res.text)
        time.sleep(1)
        token_iauth_new = get_iauth_token.get_token_iauth_new()
        time.sleep(1)
        payload = {'appId': iauth_appid, 'token': token_iauth_new}
        res = requests.get(url, params=json.dumps(payload), data=body)
        print('更新token_iauth后，返回结果为[{}]'.format(res.text))
    else:
        print('最终获取到pd对应接口的信息')
    return res.text


def get_pd_info_by_device(device):
    path = '/open-api/v2/pd-openapi/openApiService/findProjectByDevice'
    return requests_pd_auto(path, {'device': device})


def get_need_sleep_time():
    if os.path.isfile(last_time_log_filepath):
        with open(last_time_log_filepath, encoding='utf-8') as _F:
            last = _F.read()
    else:
        last = time.time()
    t = time.time() - float(last)
    with open(last_time_log_filepath, 'w', encoding='utf-8') as _F:
        _F.write('{}'.format(time.time()))
    return t