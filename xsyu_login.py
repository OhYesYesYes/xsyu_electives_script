import time
import requests
import re
import json

def do_not_access_fast(html):
    rst = re.search(r"请不要过快点击", html)
    if rst is None:
        return 0
    else:
        print("触发防爬...")
        time.sleep(4)
        return -1


def get_str_sha1_secret_str(res: str):
    import hashlib
    """
    使用sha1加密算法，返回str加密后的字符串
    """
    sha = hashlib.sha1(res.encode('utf-8'))
    encrypts = sha.hexdigest()
    print(encrypts)
    return encrypts


def get_hash_head(html: str):
    print("匹配哈希加密头部")
    search_obj = re.search(r'CryptoJS.SHA1\([\S]+', html)
    if search_obj:
        return search_obj.group(0).replace("CryptoJS.SHA1(", "").replace("'", "")
    else:
        print("没有找到")
        return -1


def login_action(usr: str, passwd: str):
    print("请求登陆界面...")
    url = 'http://jwxt.xsyu.edu.cn/eams/login.action'
    s = requests.session()
    r = s.get(url)
    set_cookie = r.headers['Set-Cookie']
    hash_str_head = get_hash_head(r.text)
    if hash_str_head != -1:
        h_passwd = get_str_sha1_secret_str(hash_str_head + passwd)
        print("提交表单...")
        time.sleep(4)
        post_data = {
            "username": usr,
            "passText": "请输入密码",
            "password": h_passwd,
            "encodedPassword": "",
            "session_locale": "zh_CN"
        }
        while True:
            r = s.post(url, data=post_data)
            if do_not_access_fast(r.text) == 0:
                break
    return set_cookie


def get_cookie(usr: str, passwd: str, semester_id=142):
    set_cookie = login_action(usr, passwd).split(";")
    cookie = "semester.id=" + str(semester_id) + "; " + set_cookie[0]+";"
    print("得到cookie:"+cookie)
    return cookie