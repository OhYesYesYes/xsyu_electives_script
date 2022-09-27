import time
import requests
import re
import json
import datetime


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


def get_cookie(usr: str, passwd: str):
    set_cookie = login_action(usr, passwd).split(";")
    cookie =set_cookie[0] + ";"
    print("得到cookie:" + cookie)
    return cookie


def progress(place, end_place, time_str="", width=50):
    '''
    打印进度条
    :param place: 目前的进度位置，类型为数字，不能为0
    :param end_place: 结束位置，类型为数字
    :param time_str: 可选择打印实花费时间和剩余时间，建议配合get_remaining_time使用
    :param width: 进度条宽度
    '''
    percent = place / end_place
    percent = percent * 100
    if percent >= 100:
        percent = 100
    show_str = ('[%%-%ds]' % width) % (int(width * percent / 100) * "#")  # 字符串拼接的嵌套使用
    print('\r%s %5.2f%% %s' % (show_str, percent, time_str), end='')

    if percent == 100:
        print('\n')


def print_remaining_time(time_beg, time_now, place, end_place):
    '''
    直接打印花费时间，剩余时间按
    :param time_beg: 开始的时间，time_beg = datetime.datetime.now()获得
    :param time_now: 现在的时间，time_now = datetime.datetime.now()获得
    :param place: 现在进度的位置，类型为数字，不能为0
    :param end_place: 结束的位置，类型为数字
    :return:
    '''
    #

    # 定义空时间
    tmep_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
    # 计算进度
    persent = place / end_place
    # 计算花费时间
    delta = time_now - time_beg
    # 计算剩余时间
    remnant = delta / persent - delta
    # 格式化花费时间
    delta = tmep_time + delta
    # 格式化剩余时间
    remnant = tmep_time + remnant
    print('\r %s  预计还剩: %s' % (delta.strftime('%H:%M:%S'), remnant.strftime('%H:%M:%S')), end='')


def get_remaining_time(time_beg, time_now, place, end_place):
    '''
    返回花费时间，剩余时间按
    :param time_beg: 开始的时间，time_beg = datetime.datetime.now()获得
    :param time_now: 现在的时间，time_now = datetime.datetime.now()获得
    :param place: 现在进度的位置，类型为数字，不能为0
    :param end_place: 结束的位置，类型为数字
    :return:
    '''

    # 定义空时间
    tmep_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
    # 计算进度
    persent = place / end_place
    # 计算花费时间
    delta = time_now - time_beg
    # 计算剩余时间
    remnant = delta / persent - delta
    # 格式化花费时间
    delta = tmep_time + delta
    # 格式化剩余时间
    remnant = tmep_time + remnant

    rst = ' 花费: %s  预计还剩: %s' % (delta.strftime('%H:%M:%S'), remnant.strftime('%H:%M:%S'))
    return rst


def waiting(text, times, max_symbol_num=5):
    '''
    手动等待,打印等待效果
    :param text: 文本
    :param times: 等待次数,默认3
    :param max_symbol_num: 动画圆点最大个数,默认5个
    '''
    symbol = '.'
    times = times % max_symbol_num
    for i in range(times + 1):
        symbol = symbol + '.'
        if symbol == ('.' * (max_symbol_num + 1)):
            symbol = '.'
    print('\r{}{}'.format(text, symbol), end='')

