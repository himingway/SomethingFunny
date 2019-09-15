#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re
from bs4 import BeautifulSoup
import requests
import time
from PIL import Image
import threading


class AutoDiscuz:
    LOGIN_PRE = "/member.php?mod=logging&action=login"
    LOGIN_CODE = "/misc.php?mod=seccode&action=update&idhash=cSHPWGkw&modid=member::loggin"
    LOGIN_URL = "/member.php?mod=logging&action=login&loginsubmit=yes"
    LOGIN_POST = {"username": "", "password": "", "seccodeverify": ""}

    def __init__(self, forum_url, user_name, password):
        """初始化论坛 url、用户名、密码和代理服务器."""
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
        self.header2 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "http://bbs.eetop.cn/misc.php?mod=seccode&action=update&idhash=cSHPWGkw&modid=member::loggin"}
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
        url_code = self.forum_url + AutoDiscuz.LOGIN_CODE
        url = self.forum_url + AutoDiscuz.LOGIN_URL
        AutoDiscuz.LOGIN_POST["username"] = self.user_name
        AutoDiscuz.LOGIN_POST["password"] = self.password
        req = self.session.post(url, data=AutoDiscuz.LOGIN_POST)

        if self.user_name in req.text:
            self.is_login = True
            if self.get_formhash():
                logging.info("Login success!")
                return
        else:
            logging.error("Login faild!")
            if self.is_login:
                self.is_login = False
                return
            req = self.session.post(url_code, headers=self.header)
            soup = BeautifulSoup(req.text, 'lxml')
            info = soup.select("#vseccode_cSHPWGkw img[src]")[0].get("src")
            req = self.session.post(self.forum_url + "/" + info, headers=self.header2)
            with open('./captcha.jpg', 'wb') as f:
                f.write(req.content)
            img = Image.open('./captcha.jpg')
            img_thread = threading.Thread(target=img.show, daemon=True)
            img_thread.start()
            capt = input('请输入图片里的验证码：')
            AutoDiscuz.LOGIN_POST["seccodeverify"] = capt

    def get_formhash(self):
        """获取 formhash."""
        req = self.session.get(self.forum_url)
        rows = re.findall(r"formhash=(.*?)\"", req.text)
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
    while True:
        auto_discuz.login()
        if auto_discuz.is_login:
            auto_discuz.check_in()
            time.sleep(5 * 60 * 59)
        else:
            requests.post("https://sc.ftqq.com/【Pushbear Key】.send?text=eetop登录")
            print("break")
            break


if __name__ == "__main__":
        main()
        # time.sleep(5 * 60 * 59)
