#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re
from bs4 import BeautifulSoup
import requests
import time


class AutoDiscuz:
    LOGIN_URL = "/member.php?mod=logging&action=login&loginsubmit=yes"
    LOGIN_POST = {"username": "", "password": ""}

    def __init__(self, forum_url, user_name, password):
        """初始化论坛 url、用户名、密码和代理服务器."""
        self.forum_url = forum_url
        self.loginfield = "username"
        self.user_name = user_name
        self.password = password
        self.questionid = 0
        self.answer = None
        self.formhash = None
        self.is_login = False
        self.session = requests.Session()
        logging.basicConfig(level=logging.INFO,
                            format="[%(levelname)1.1s %(asctime)s] %(message)s")

    def login(self):
        """登录论坛."""
        url = self.forum_url + AutoDiscuz.LOGIN_URL
        AutoDiscuz.LOGIN_POST["username"] = self.user_name
        AutoDiscuz.LOGIN_POST["password"] = self.password
        req = self.session.post(url, data=AutoDiscuz.LOGIN_POST)
        cookies = req.cookies.get_dict()
        self.sid = cookies["dx_1c1c_sid"]
        # print(req.content.decode('utf-8'))
        if self.user_name in req.text:
            self.is_login = True
            if self.get_formhash():
                logging.info("Login success!")
                return
        logging.error("Login faild!")

    def get_formhash(self):
        """获取 formhash."""
        req = self.session.get(self.forum_url)
        rows = re.findall(r"formhash=(.*?)\"", req.text)
        print(rows)
        if len(rows) != 0:
            self.formhash = rows[0]
            logging.info("Formhash is: " + self.formhash)
            return True
        else:
            logging.error("None formhash!")
            return False

    def check_in(self):
        url = self.forum_url + \
            "/home.php?mod=task&do=apply&id=14"
        content = self.session.get(url).text
        soup = BeautifulSoup(content, 'lxml')
        info = soup.select(".f_c div p")[0].get_text()
        print(info)

def main():
    auto_discuz = AutoDiscuz("http://bbs.eetop.cn", "用户名", "密码")
    auto_discuz.login()
    if auto_discuz.is_login:
        auto_discuz.check_in()

if __name__ == "__main__":
    while True:
        main()
        main()
        time.sleep(5*60*59)
