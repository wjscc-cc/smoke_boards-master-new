import json
import re
import time
from data import *
import com.get_cookies2 as get_cookies
from omni_spyder import data


def catch_result(f_result):
    f_task = open("task.txt", "r", encoding='utf8')
    task_list = f_task.readlines()
    result_dir = []
    case_cn_dir = data.case_cn_dir
    case_gl_dir = data.case_gl_dir
    # 获取omni任务当前运行状态
    num = 0
    for task in task_list:
        num = num + 1
        info = task.split("\t")
        product = info[0]

        detail_list = []

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
                    fail_list = re.findall('<tr style="color: red"><td>.*?</td></tr>', info_response.text)

                    if len(fail_list) > 0:
                        if info[1] == 'CN':
                            for fail_line in fail_list:
                                fail_numb = fail_line.split('<td>')[1].strip('</td>')
                                if fail_numb in case_cn_dir:
                                    case_cn_dir[fail_numb] = case_cn_dir[fail_numb] + 1
                        else:
                            for fail_line in fail_list:
                                fail_numb = fail_line.split('<td>')[1].strip('</td>')
                                if fail_numb in case_gl_dir:
                                    case_gl_dir[fail_numb] = case_gl_dir[fail_numb] + 1
                    total_num = re.search("总计 \d+", reportInfo).group()[3:]
                    pass_num = re.search("pass \d+", reportInfo).group()[5:]
                    fail_num = re.search("fail \d+", reportInfo).group()[5:]
                    result = total_num + "\\" + fail_num
                    numb = 'NA'
                    phone = 'NA'
                    for i in data_list:

                        if info[0] in i and info[1] in i:
                            numb = i[3]
                            phone = i[1]
                    detail_list.append(int(fail_num))
                    detail_list.append(phone)
                    detail_list.append(numb)
                    detail_list.extend(info)

                    result_dir.append(detail_list)



                else:
                    result = "NOT INFO"
            else:
                result = "Running"
        f_result.write(result)
        f_result.write(("\n"))
        print(result)
    result_dir.sort(key=lambda x: x[0], reverse=True)
    time.sleep(1)
    #机器失败case数量排序
    title = ['失败数量\t', '机型\t', '节点\t', '内部代码\t', '地区\t', '安卓版本\t', '日期\t', '任务链接\n']
    with open('机型失败case数量排序.txt', 'a+', encoding='utf8') as f_result_or:
        f_result_or.truncate(0)
        for i in title:
            f_result_or.write(i)
        for j in result_dir:
            for k in j:
                f_result_or.write(f'{k}\t')
#国内失败case字典排序
    sorted_by_value_cn = dict(sorted(case_cn_dir.items(), key=lambda item: item[1], reverse=True))
#国际失败case字典排序
    sorted_by_value_gl = dict(sorted(case_gl_dir.items(), key=lambda item: item[1], reverse=True))
#写入国内case失败排行
    with open('fail_cn.txt', 'a+', encoding='utf8') as f_fail_cn:
        f_fail_cn.truncate(0)
        for i in sorted_by_value_cn:
            f_fail_cn.write(f'{i}--{sorted_by_value_cn[i]}--{data.cn_case_check_dir[i]}')
            f_fail_cn.write('\n')
    # 写入国际case失败排行
    with open('fail_gl.txt', 'a+', encoding='utf8') as f_fail_gl:
        f_fail_gl.truncate(0)
        for i in sorted_by_value_gl:
            f_fail_gl.write(f'{i}--{sorted_by_value_gl[i]}--{data.gl_case_check_dir[i]}')
            f_fail_gl.write('\n')
