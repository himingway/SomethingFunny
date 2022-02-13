#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re
from bs4 import BeautifulSoup
import requests
import sys
import time
from PIL import Image
import threading


class AutoDiscuz:

    def __init__(self, forum_url, user_name, password):
        """初始化论坛 url、用户名、密码和代理服务器."""
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.4",
            "Referer": "https://bbs.eetop.cn/member.php?mod=logging&action=login"
            ""}

        self.header2 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.4",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "https://bbs.eetop.cn/member.php?mod=logging&action=login"}

        self.forum_url = forum_url
        self.is_login = False
        self.post_data = {"username": user_name,
                          "password": password,
                          "seccodemodid": "member::logging",
                          "loginfield": 'username'
                          }
        self.seccode = ''
        self.formhash = ''
        self.loginhash = ''
        self.session = requests.Session()
        #logging.basicConfig()  # 初始化 logging，否则不会看到任何 requests 的输出。
        #logging.getLogger().setLevel(logging.DEBUG)
        #requests_log = logging.getLogger("requests.packages.urllib3")
        #requests_log.setLevel(logging.DEBUG)
        #requests_log.propagate = True

    def login(self):
        """登录论坛."""
        url_start = self.forum_url + "/member.php?mod=logging&action=login"
        req = self.session.get(url_start, headers=self.header)
        '''找到hash'''
        soup = BeautifulSoup(req.text, 'lxml')
        find0 = re.findall(r'\"seccode_(.*?)\"', req.text)
        find1 = re.findall(r'name=\"formhash\" value=\"(.*?)\"', req.text)
        find2 = re.findall(r'loginhash=(.*?)\"', req.text)
        if find0 and find1:
            self.seccode = find0[0]
            self.formhash = find1[0]
            self.loginhash = find2[0]
        else:
            print("can't find seccode or formhash")
            sys.exit(2)
        url_seccode = self.forum_url + '/misc.php?mod=seccode&action=update&idhash=%s&modid=member::logging' %self.seccode
        req = self.session.get(url_seccode, headers=self.header)
        '''找到验证码图片'''
        find = re.findall(r'src=\"(misc\.php\?.*?)\"', req.text)
        if find:
            seccode_pic_url = find[0]
        else:
            print("can't find seccode")
            sys.exit(2)
        url_seccode_pic = self.forum_url + '/' + seccode_pic_url
        print(url_seccode_pic)
        self.session.headers.clear()
        self.header2['Referer'] = url_seccode
        req = self.session.get(url_seccode_pic, headers=self.header2)
        with open('./captcha.jpg', 'wb') as f:
            f.write(req.content)
        capt = input('请输入图片里的验证码：')
        '''验证验证码是否正确'''
        url_verif_seccode = self.forum_url + '/misc.php?mod=seccode&action=check&inajax=1&modid=member::logging&idhash=%s&secverify=%s' %(self.seccode, capt)
        req = self.session.get(url_verif_seccode, headers=self.header)
        print(req.content)
        '''登录'''
        url_login = self.forum_url + "/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=%s" %self.loginhash
        print(url_login)
        self.post_data["formhash"] = self.formhash
        self.post_data["seccodehash"] = self.seccode
        self.post_data["seccodeverify"] = capt
        self.post_data["loginsubmit"] = 'true'
        self.post_data["referer"] = 'https://bbs.eetop.cn/'
        print(self.post_data)
        self.session.headers.clear()
        req = self.session.post(url_login, data=self.post_data, headers=self.header)
        # url_code = self.forum_url + AutoDiscuz.LOGIN_CODE
        # url = self.forum_url + AutoDiscuz.LOGIN_URL
        # AutoDiscuz.LOGIN_POST["username"] = self.user_name
        # AutoDiscuz.LOGIN_POST["password"] = self.password
        # print(AutoDiscuz.LOGIN_POST)
        # req = self.session.post(url, data=AutoDiscuz.LOGIN_POST)
        # match = re.findall(r'name=\"formhash\" value=\"(.*?)\"', req.text)
        # if match:
        #    AutoDiscuz.LOGIN_POST["formhash"] = match[0]
        # else:
        #    print('can find formhash')
        #    sys.exit(2)
        # if self.user_name in req.text:
        #    self.is_login = True
        #    if self.get_formhash():
        #        logging.info("Login success!")
        #        return
        # else:
        #    logging.error("Login faild!")
        #    if self.is_login:
        #        self.is_login = False
        #        return
        #    req = self.session.post(url_code, headers=self.header)
        #    match = re.findall("\'seccode_(.*?)\'", req.text)
        #    if match:
        #        AutoDiscuz.LOGIN_POST["seccode"] = match[0]
        #    else:
        #        print('can find seccode')
        #        sys.exit(2)
        #    soup = BeautifulSoup(req.text, 'lxml')
        #    info = soup.select("#vseccode_cSHPWGkw img[src]")[0].get("src")
        #    req = self.session.post(self.forum_url + "/" + info, headers=self.header2)
        #    with open('./captcha.jpg', 'wb') as f:
        #        f.write(req.content)
        #    #img = Image.open('./captcha.jpg')
        #    #img_thread = threading.Thread(target=img.show, daemon=True)
        #    #img_thread.start()
        #    capt = input('请输入图片里的验证码：')
        #    AutoDiscuz.LOGIN_POST["seccodeverify"] = capt
        #    AutoDiscuz.LOGIN_POST["loginfield"] = 'username'

    def check_in(self):
        url = self.forum_url + \
              "/home.php?mod=task&do=apply&id=14"
        content = self.session.get(url).text
        soup = BeautifulSoup(content, 'lxml')
        info = soup.select(".f_c div p")[0].get_text()
        if info:
            self.is_login = True
            print(info)
        else:
            self.is_login = False


def main():
    auto_discuz = AutoDiscuz("https://bbs.eetop.cn", "【UserName】", "【Password】")
    auto_discuz.login()
    while True:
        auto_discuz.check_in()
        if auto_discuz.is_login:
           time.sleep(5 * 60 * 59)
        else:
           print("break")
           requests.post("https://sc.ftqq.com/【KEY】.send?title=eetop登录")
           break


if __name__ == "__main__":
    main()
    # time.sleep(5 * 60 * 59)
