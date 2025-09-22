import time
import spyder_links
import spyder_results

if input('执行任务链接抓取\n确认执行输入Yes&&跳过输入任意键') == 'Yes':
    with open('task.txt', 'a+', encoding='utf8') as f_task:
        f_task.truncate(0)
        spyder_links.catch_links(f_task)

time.sleep(1)
if input('执行任务结果抓取\n确认执行输入Yes&&跳过输入任意键') == 'Yes':
    with open('result.txt', 'a+', encoding='utf8') as f_result:
        f_result.truncate(0)
        spyder_results.catch_result(f_result)
