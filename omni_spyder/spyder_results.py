import json
import time
import com.get_cookies2 as get_cookies
import re


def catch_result(f_result):
    f_task = open("task.txt", "r", encoding='latin-1')
    task_list = f_task.readlines()

    # 获取omni任务当前运行状态
    num = 0
    for task in task_list:
        num = num + 1
        info = task.split("\t")
        product = info[0]
        omniLink_s = info[6].strip()
        print(num, product, end="---")
        if omniLink_s == "NA":
            result = "NA"
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
                else:
                    result = "NOT INFO"
            else:
                result = "RUNNING/QUEUING"
        f_result.write(result)
        f_result.write(("\n"))
        print(result)
    # time.sleep(1)
