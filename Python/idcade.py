# !/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import time
from bs4 import BeautifulSoup

# pip install beautifulsoup4
# pip install lxml

class SFZ(object):
    """
    山东身份证办证进度爬虫，server酱推送微信办证进度
    """

    def __init__(self, idcard):
        # 初始化
        self.url = "http://dzzw.sdems.com/idcard/index.php?s=/idcard/index/selinfo.html"
        self.idcard = idcard
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
            "Referer": "http://dzzw.sdems.com/idcard/"
        }

    def make_data(self):
        data = {
            "idcard": self.idcard
        }
        return data

    def get_content(self, data):
        # 发送请求获取响应
        response = requests.post(
            url=self.url,
            headers=self.headers,
            data=data
        )
        return response

    def run(self):
        """运行程序"""
        # 构建参数
        data = self.make_data()
        content = self.get_content(data)
        if content.status_code == 200:
            soup = BeautifulSoup(content.content, 'lxml')
            info = soup.select(".ems_id_box div")[0].get_text()
            # print(info)
            return info
        else:
            return 0


class ServerChan(object):
    def __init__(self, key):
        self.api = "https://sc.ftqq.com/" + key + ".send"
        self.text = "身份证办证信息"

    def make_data(self, desp):
        data = {
            "text": self.text,
            "desp": desp
        }
        return data

    def send_msg(self, api, data):
        response = requests.post(api, data=data)
        return response

    def run(self, desp):
        data = self.make_data(desp)
        send = self.send_msg(self.api, data)


def in_time_range(ranges):
    now = time.strptime(time.strftime("%H%M%S"), "%H%M%S")
    ranges = ranges.split(",")
    for range in ranges:
        r = range.split("-")
        if time.strptime(r[0], "%H%M%S") <= now <= time.strptime(r[1], "%H%M%S") or \
                time.strptime(r[0], "%H%M%S") >= now >= time.strptime(r[1], "%H%M%S"):
            return True
    return False


if __name__ == '__main__':
    msg = []
    sfz = SFZ("370xxxxxxxxxxxxxxx") # 身份证号码，例"370xxxxxxxxxxxxxxx"
    ServerChan = ServerChan(
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx") # Server酱SCKEY，http://sc.ftqq.com
    while True:
        if in_time_range("080000-210000"): # 查询时间：早八点到晚六点
            info = sfz.run()
            print(info)
            if not info:
                ServerChan.run("服务器挂了")
                break
            elif info not in msg:
                ServerChan.run(info)
                msg.append(info)
        time.sleep(60)
