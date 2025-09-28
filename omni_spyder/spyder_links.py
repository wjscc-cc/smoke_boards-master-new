import json
import time

import com.get_cookies2 as get_cookies




def get_today(dis=0):
    today_list=[]
    now_time = time.localtime(time.time() + dis * 24 * 60 * 60 - 1)
    _today1 = '{}.{}.{}'.format(str(now_time.tm_year)[-2:], now_time.tm_mon, now_time.tm_mday)
    _today2 = time.strftime("%Y%m%d", time.localtime())[2:]
    today_list.append(_today1)
    today_list.append(_today2)
    return today_list

def catch_links(f_task):
    ci_id_list = []
    with open('ci_id', 'r') as f:
        for i in f:
            if i:
                ci_id_list.append(i.strip())

    # 获取omni任务链接
    for ci_id in ci_id_list:
        today = get_today()
        ci_url = 'https://postci.pt.xiaomi.com/s/pipeline/{}/recentRomBuilds?loadTimes=1'.format(ci_id)
        # print(ci_url)
        ci_resp = get_cookies.request_auto(ci_url)
        ci_task_info = {}
        try:
            ci_task_data = json.loads(ci_resp.text)['data']
        except:
            ci_task_data=None
        # print(ci_task_data)
        if not ci_task_data:
            product = "NA"
            region = "NA"
            androidCode = "NA"
            version = "NA"
        else:
            product = ci_task_data[0]['product']
            region = ci_task_data[0]['region']['name']
            androidCode = ci_task_data[0]['androidCode']
        # 检查获取到最新任务是否为当天任务
        if ci_task_data:
            if today[0] in ci_task_data[0]['version'] or today[1] in ci_task_data[0]['version']:
                ci_task_info = ci_task_data
                version = today[0]
            else:
                version = "NA"
        f_task.write(product)
        f_task.write("\t")
        f_task.write(region)
        f_task.write("\t")
        f_task.write(androidCode)
        f_task.write("\t")
        f_task.write(version)
        f_task.write("\t")
        # 若是，输出任务链接；若否，输出NA
        if not ci_task_info:
            # f_omniLink_s.write("NA")
            # f_omniLink_s.write("\n")
            f_task.write("NA")
            f_task.write("\t")
            f_task.write("NA")
            f_task.write("\t")
            f_task.write("NA")
            f_task.write("\n")
            print("NA")
        else:
            buildId = ci_task_info[0]['buildId']
            build_url = 'https://postci.pt.xiaomi.com/s/test/list/oneBuild?buildId={}&omniOneDirectoryId=53&omniSecondDirectoryId=131&result=&page=1&size=9999999&priorityIds='.format(buildId)
            build_resp = get_cookies.request_auto(build_url)
            build_data = json.loads(build_resp.text)['data']
            omniLink_s = build_data[0]['omniLink']
            autoResult = build_data[0]['autoResult']
            if autoResult == "Failed" or autoResult == "Passed":
                createdTime = build_data[0]['createdTime']
                executedTime = build_data[0]['executedTime']
            else:
                createdTime = 0
                executedTime = 0
            execut_Time = round((executedTime - createdTime)/60000,1)
            # f_omniLink_s.write(omniLink_s)
            # f_omniLink_s.write("\n")
            f_task.write(autoResult)
            f_task.write("\t")
            f_task.write(str(execut_Time))
            f_task.write("\t")
            f_task.write(omniLink_s)
            f_task.write("\n")
            print(omniLink_s)
        time.sleep(1)
