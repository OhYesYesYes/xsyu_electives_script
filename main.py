import json
import re
import time
from time import sleep
import requests
from soupsieve import select
from xsyu_login import get_cookie, waiting
import os

def get_config(path="./config1.json"):
    info_dict = {}
    with open(path, "r", encoding="utf-8") as f:
        info_dict = json.load(f)
    f.close()
    return info_dict


def get_profileid(cookies):
    headers = {"Cookie": cookies}
    # 获得profileId
    url_for_id = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse.action"
    re_id = requests.get(url=url_for_id, verify=False, headers=headers)
    while (re_id.status_code != 200):
        re_id = requests.get(url=url_for_id, verify=False, headers=headers)
    id_str = re_id.text.split("confirmElection(")
    profileid = id_str[1][:4]
    return profileid


def grap_class(cookies):
    headers = {"Cookie": cookies}
    # 更快的方法是提前抓取profile填入
    profileid = get_profileid(cookies)
    # 循环到选课时间
    url1 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id=" + profileid
    url2 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!data.action?profileId=" + profileid
    requests.get(url=url1, headers=headers)  # 求稳
    re_data = requests.get(url=url2, headers=headers)
    while re_data.status_code != 200:
        requests.get(url=url1, headers=headers)
        sleep(1)
        re_data = requests.get(url=url2, headers=headers)
        print("正在运行中...状态码: ", re_data.status_code)
    text = re_data.text[22:-1]
    list = text.split(",{id")
    lists = []
    white_list = get_config()["white_list"]
    black_list = get_config()["black_list"]
    # name是课程名 ， teachers是老师
    wnp = get_config()["wnp"]
    bnp = get_config()["bnp"]

    # 处理json数据
    for i in list:
        i = "{'id'" + i
        i = i.replace("'", "\"")
        i = re.sub(r',(.*?):', r',"\1":', i)
        i = i[:i.index(',"remark')] + "}"
        jsons = json.loads(i)
        # 白名单
        q = False
        for j in white_list:
            q = True
            if (jsons[wnp].find(j) != -1):
                lists.append(jsons['id'])
                print(jsons[wnp])
                break
        if (q):
            continue
        # 黑名单
        p = True
        for k in black_list:
            if (jsons[bnp].find(k) != -1):
                p = False
                break
        if (p):
            lists.append(jsons['id'])
            print(jsons[bnp])

    # 抢课
    url3 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!batchOperator.action?profileId=" + profileid

    num_flag = 0
    while True:
        if num_flag == 5:
            num_flag = 0
        for i in lists:
            postdata = {"optype": "true",
                        "operator0": str(i) + ":true:0"}
            rew = requests.session().post(url=url3, verify=False,
                                          data=postdata, headers=headers)
            if rew.text.find('失败') < 0:
                print("抢课成功!")
        waiting("正在执行抢课,请等待", num_flag)
        num_flag += 1


def main():
    try:
        config_info = get_config()
    except:
        print("没有找到config.json配置文件，请将配置文件放在同一目录!")

        os.system("pause")
        return
    cookies = get_cookie(
        config_info["student_id"], config_info["password"], config_info["semester_id"])
    grap_class(cookies)


# //2021级1616
# //2020级1613
# //2019级1611
# //2022/3/29
if __name__ == "__main__":
    main()
