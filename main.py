import json
import re
import time
from time import sleep
import requests
from soupsieve import select
from xsyu_login import get_cookie, waiting, do_not_access_fast
import os


def get_config(path="./config.json"):
    info_dict = {}
    with open(path, "r", encoding="utf-8") as f:
        info_dict = json.load(f)
    f.close()
    return info_dict


def get_profileid(cookies):
    headers = {"Cookie": cookies}
    # 获得profileId
    url_for_id = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse.action"
    re_id = ""
    while True:
        re_id = requests.get(url=url_for_id, headers=headers)
        if do_not_access_fast(re_id.text) != 0 and re_id.status_code != 200:
            re_id = requests.get(url=url_for_id, headers=headers)
            print("触发防爬或请求错误,正在重试...")
        else:
            break
    id_str = re_id.text.split("confirmElection(")
    profileid = id_str[1][:4]
    return profileid


def grap_class(cookies):
    headers = {"Cookie": cookies}
    # 更快的方法是提前抓取profile填入
    profileid = "1611"
    try:
        profileid = get_profileid(cookies)
        print("你的profileid为{},请记住,学校服务器有时可能无法得到profileid,届时会转为手动输入!".format(profileid))
        print("你的profileid为{},请记住,学校服务器有时可能无法得到profileid,届时会转为手动输入!".format(profileid))
        print("你的profileid为{},请记住,学校服务器有时可能无法得到profileid,届时会转为手动输入!".format(profileid))
    except:
        print("发生了错误导致无法请求到profileid，可能是账户密码没有配置或者错误!也可能是教务系统限制了登陆人数")
        choose = input("需要手动输入吗?[N/y]:")
        if choose != "y" and choose != "Y":
            return
        else:
            print("2021级: 1616")
            print("2020级: 1613")
            print("2019级: 1611")
            print("2022/3/29统计")
            profileid = input("请输入profileid:")
            profileid = str(profileid)
    # 循环到选课时间
    url1 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id=" + profileid
    url2 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!data.action?profileId=" + profileid
    requests.get(url=url1, headers=headers)  # 求稳

    re_data = requests.get(url=url2, headers=headers)
    while re_data.status_code != 200 and do_not_access_fast(re_data.text) != 0:
        requests.get(url=url1, headers=headers)
        sleep(1)
        re_data = requests.get(url=url2, headers=headers)
        print("正在运行等待中...状态码: ", re_data.status_code)
    text = re_data.text[22:-1]
    list = text.split(",{id")
    lists = []
    white_list = get_config()["white_list"]
    black_list = get_config()["black_list"]
    # name是课程名 ， teachers是老师
    wnp = get_config()["wnp"]
    bnp = get_config()["bnp"]

    # 处理json数据
    try:
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
    except:
        print("发生了错误,可能是profileid错误")
        return

    # 抢课
    url3 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!batchOperator.action?profileId=" + profileid
    num_flag = 0
    while True:
        while_flag = 0
        if while_flag == 5:
            print("多次抢课失败，可能是白名单列表的课程没有能选课的，结束抢课")
            os.system("pause")
            return
        if num_flag == 5:
            num_flag = 0
        for i in lists:
            postdata = {"optype": "true",
                        "operator0": str(i) + ":true:0"}
            rew = ""
            while True:
                rew = requests.session().post(url=url3,
                                              data=postdata, headers=headers)
                if do_not_access_fast(rew.text) != 0:
                    continue
                else:
                    break
            # print(rew.text)
            if rew.text.find('失败:该课程可供选择名额已满，请选择其他课程') > 0:
                print(i, "课程可供选择名额已满")
            elif rew.text.find('失败:人数已满') > 0:
                print(i, "课程人数已满")
            elif rew.text.find('失败:你已经选过') > 0:
                print("抢课失败！你已经选过，请取消选课之后再试!")
                return
            elif rew.text.find('失败') < 0:
                print("抢课成功!")
                return
            print("抢课失败!正在重试")
            print(rew.text)
        num_flag += 1
        while_flag += 1


def main():
    try:
        config_info = get_config()
    except:
        print("没有找到config.json配置文件，请将配置文件放在同一目录!")
        print("也有可能你的config.json文件配置错误，请检查！注意在[]中添加内容时需要添加引号以及使用utf-8")
        os.system("pause")
        return
    cookies = get_cookie(config_info["student_id"], config_info["password"], config_info["semester_id"])
    # cookies = "cookie:semester.id=162; JSESSIONID=A4B6BBCEA8879F59D6ED14AC9AD28864.-node1;"
    grap_class(cookies)


# //2021级1616
# //2020级1613
# //2019级1611
# //2022/3/29
if __name__ == "__main__":
    main()
