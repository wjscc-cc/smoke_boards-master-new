import re

str_0 = '11356541-1461304/flare_global_OS2.0.250813.1.VHXMIXM_11356541_report'
str_1 = 'http://omni.pt.miui.srv/views/tempResult/11356541-1461304/flare_global_OS2.0.250813.1.VHXMIXM_11356541_report/testCase/33989/result.html'
STR_2 = 'http://omni.pt.miui.srv/execution/resultDetail?url=http://cnbj1-fds.api.xiaomi.net/omni.upload/execution_result/11356541/1461304/flare_global_OS2.0.250813.1.VHXMIXM_11356541_report.zip&executionId=11356541'
str_list=str_0.split('/')
str_0_2=f"{re.sub('-','/',str_list[0])}/{str_list[1]}"
zipionId=str_list[0].split('-')[0]
str_2=f"http://omni.pt.miui.srv/execution/resultDetail?url=http://cnbj1-fds.api.xiaomi.net/omni.upload/execution_result/{str_0_2}.zip&executionId={zipionId}"
