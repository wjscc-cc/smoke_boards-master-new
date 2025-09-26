import re
from data import *
import com.get_cookies2 as get_cookies

case_cn_dir = case_cn_dir
get_cookies.request_auto(
    'http://omni.pt.miui.srv/execution/result/download?url=http://cnbj1-fds.api.xiaomi.net/omni.upload/execution_result/11591660/1701514/pandora_OS3.0.250925.1.WBLCNXM_11591660_report.zip&executionId=11591660')
info_response = get_cookies.request_auto(
    'http://omni.pt.miui.srv/views/tempResult/11591660-1701514/pandora_OS3.0.250925.1.WBLCNXM_11591660_report/testCase/33989/result.html')
reportInfo = info_response.text
fail_list = re.findall('<tr style="color: red"><td>.*?</td></tr>', info_response.text)
for fail_line in fail_list:
    fail_numb = fail_line.split('<td>')[1].strip('</td>')
    if fail_numb in case_cn_dir:
        case_cn_dir[fail_numb] = case_cn_dir[fail_numb] + 1
sorted_by_value = dict(sorted( case_cn_dir.items(), key=lambda item: item[1],reverse=True))
# case_cn_dir = sorted(case_cn_dir, key=lambda x: case_cn_dir[x], reverse=True)
print(case_cn_dir)
with open('fail_cn.txt', 'a+', encoding='utf8') as f_fail_cn:
    f_fail_cn.truncate(0)
    for i in sorted_by_value:
        f_fail_cn.write(f'{i}:{sorted_by_value[i]}')
        f_fail_cn.write('\n')
