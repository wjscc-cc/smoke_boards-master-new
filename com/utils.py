import json
import time
from datetime import datetime, timedelta

import requests


def get_today(dis=0):
    now_time = time.localtime(time.time() + dis * 24 * 60 * 60 - 1)
    _today = '{}.{}.{}'.format(str(now_time.tm_year)[-2:], now_time.tm_mon, now_time.tm_mday)
    return _today


def convert_date_to_timestamp(date_string):
    # 1. 解析日期字符串
    date_format = "%y.%m.%d"
    date_obj = datetime.strptime(date_string, date_format)

    # 2. 将日期对象转换为时间戳（秒）
    timestamp_in_seconds = int(date_obj.timestamp())

    # 3. 将时间戳转换为毫秒并转换为字符串形式
    timestamp_in_milliseconds = timestamp_in_seconds * 1000
    return str(timestamp_in_milliseconds)


def date_to_timestamp_range(date_str):
    # 解析日期字符串为datetime对象
    date_format = "%y.%m.%d"
    date_obj = datetime.strptime(date_str, date_format)

    # 获取当天的开始时间和结束时间
    start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(microseconds=1)

    # 转换为时间戳
    start_timestamp = int(start_of_day.timestamp() * 1000)  # 转换为毫秒
    end_timestamp = int(end_of_day.timestamp() * 1000)  # 转换为毫秒

    return start_timestamp, end_timestamp


def send_mail(mail_title, mail_to, mail_cc, mail_body):
    print("send_mail获取到邮件信息为：")
    for i in mail_title, mail_to, mail_cc, mail_body:
        print(i)
    if ',' in mail_cc:
        mail_cc = mail_cc.split(',')
    elif ';' in mail_cc:
        mail_cc = mail_cc.split(';')
    else:
        mail_cc = [mail_cc]
    if ',' in mail_to:
        mail_to = mail_to.split(',')
    elif ';' in mail_to:
        mail_to = mail_to.split(';')
    else:
        mail_to = [mail_to]
    import smtplib
    from email.mime.text import MIMEText
    # 以前读取表格的代码, 先不删
    # # 获取token
    # url = 'https://open.f.mioffice.cn/open-apis/auth/v3/tenant_access_token/internal'
    # headers = {'Content-Type': 'application/json; charset=utf-8'}
    # postdata = {'app_id': 'cli_a22c141d33789062', 'app_secret': 'YldvuyO0PI183dKgKecWmgTIUpAvsBzN'}
    # res = requests.post(url=url, params=postdata, headers=headers)
    # res_json = json.loads(res.text)
    # access_token = res_json['tenant_access_token']

    msg = MIMEText(mail_body, 'html', "utf-8")
    # msg['Subject'] = "【Smoke自动化】T升级Sanity Smoke自动化每日报告_" + time.strftime("%Y.%m.%d", time.localtime())
    msg['Subject'] = mail_title
    msg['From'] = "sanity-smoke@xiaomi.com"
    msg["To"] = ','.join(mail_to)
    msg['Cc'] = ','.join(mail_cc)

    smtp = smtplib.SMTP()

    try:
        smtp.connect("smtp.mioffice.cn", port=25)
        smtp.login("sanity-smoke", "!mjjHF00")
        smtp.sendmail("sanity-smoke@xiaomi.com", mail_to + mail_cc, msg.as_string())
        print("报告发送成功", msg['Subject'])
        return "报告发送成功"
    except smtplib.SMTPException as E:
        print(E.errno)
        print(str(E))
        print("Error: 无法发送邮件")
        return "Error: 无法发送邮件"
    finally:
        smtp.quit()
        print('结束send_mail')