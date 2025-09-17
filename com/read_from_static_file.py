import os
import json

from Smoke_manager.settings import BASE_DIR

FILE_DIR = os.path.join(BASE_DIR, 'com', 'file')


def get_case_data():
    with open(os.path.join(FILE_DIR, 'sanity_case.json')) as _F:
        micase_data = json.load(_F)
    with open(os.path.join(FILE_DIR, 'sanity_case_dev.json')) as _F:
        smoke_dev_data = json.load(_F)
    data = micase_data
    for k, v in smoke_dev_data.items():
        if not data.get(k):
            data[k] = v
    return data


def get_plan(region, plan_param, branch):
    is_lite = plan_param == 'LITE'
    branch = branch.lower()
    region = region.lower()
    file_name = 'plan_{}_{}.txt'.format(branch, region)
    if is_lite:
        file_name = 'plan_lite_{}.txt'.format(region)
    if not os.path.isfile(os.path.join(FILE_DIR, file_name)):
        print('未找到文件{}'.format(os.path.join(FILE_DIR, file_name)))
        return ''
    with open(os.path.join(FILE_DIR, file_name)) as _F:
        file_txt = _F.read()
        return file_txt


def get_poj_dict():
    with open(os.path.join(FILE_DIR, 'poj_data.json')) as _F:
        return json.load(_F)


def get_smoke_task_list(group):
    # from config.cfg import group_list
    group_to_file_dict = {
        'dev': 'list_1',
        'update': 'list_2',
        'test': 'list_3',
    }
    if group_to_file_dict.get(group):
        file_path = os.path.join(FILE_DIR, group_to_file_dict.get(group))
    else:
        raise Exception("未找到该分组对应的文件group=[{}]".format(group))
    with open(file_path, 'r') as _F:
        d = _F.read()
    return d

