import json
import re
import time

import com.get_cookies2 as get_cookies


def catch_result(f_result):
    f_task = open("task.txt", "r", encoding='utf8')
    task_list = f_task.readlines()
    result_dir = {}

    # 获取omni任务当前运行状态
    num = 0
    for task in task_list:
        num = num + 1
        info = task.split("\t")
        product = info[0]
        task_url = info[6]

        detail_list = info[0:4]

        # print(detail_list)
        omniLink_s = info[6].strip()
        print(num, product, end="---")
        if omniLink_s == "NA":
            result = "未出包"
        else:
            taskId = re.search("\d+", omniLink_s).group()
            omniLink = "http://omni.pt.miui.srv/api/task/executionsInfo?taskId=" + taskId
            omni_resp = get_cookies.request_auto(omniLink)
            omni_data = json.loads(omni_resp.text)
            reportUrl = omni_data[0]["reportUrl"]

            if reportUrl != "":
                s = re.search(r'\d+/\d+/.+_report', reportUrl).group().replace("/", "-", 1)
                reportInfo_url = "http://omni.pt.miui.srv/views/tempResult/" + s + "/testCase/33989/result.html"

                str_list = s.split('/')
                str_0_2 = f"{re.sub('-', '/', str_list[0])}/{str_list[1]}"
                zipionId = str_list[0].split('-')[0]

                str_2 = f'http://omni.pt.miui.srv/execution/result/download?url=http://cnbj1-fds.api.xiaomi.net/omni.upload/execution_result/{str_0_2}.zip&executionId={zipionId}'

                try:
                    count1 = 0
                    info_response1 = get_cookies.request_auto(str_2)
                    # print(info_response1)
                    while str(info_response1) != "<Response [200]>":
                        # print(info_response1)
                        print(num, product, end="---")
                        count1 = count1 + 1
                        if count1 > 5:
                            break
                        time.sleep(10 * count1)
                        info_response1 = get_cookies.request_auto(reportInfo_url)
                except:
                    info_response1 = None

                # time.sleep(1)
                info_response = get_cookies.request_auto(reportInfo_url)
                if str(info_response) != "<Response [200]>":
                    # print(info_response)
                    print(num, product, end="---")
                    # time.sleep(10)
                    try:
                        info_response = get_cookies.request_auto(reportInfo_url)
                    except:
                        info_response = None
                if str(info_response) == "<Response [200]>":
                    reportInfo = info_response.text
                    total_num = re.search("总计 \d+", reportInfo).group()[3:]
                    pass_num = re.search("pass \d+", reportInfo).group()[5:]
                    fail_num = re.search("fail \d+", reportInfo).group()[5:]
                    result = total_num + "\\" + fail_num
                    detail_list.append(fail_num)
                    result_dir[task_url] = detail_list
                    detail_list.append(task_url)


                else:
                    result = "NOT INFO"
            else:
                result = "Running"
        f_result.write(result)
        f_result.write(("\n"))
        print(result)

    # time.sleep(1)
    title = ['内部代码\t', '地区\t', '安卓版本\t', '日期\t', '失败数量\t', '任务链接\n']
    with open('失败排序.txt', 'a+', encoding='utf8') as f_result_or:
        f_result_or.truncate(0)
        for i in title:
            f_result_or.write(i)
        for j in result_dir:
            for k in result_dir[j]:
                f_result_or.write(f'{k}\t')
