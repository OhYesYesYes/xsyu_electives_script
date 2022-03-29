import json
import re
from time import sleep
import requests
from soupsieve import select
from xsyu_login import get_cookie


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
    re_id = requests.get(url=url_for_id, verify=False, headers=headers)
    while(re_id.status_code != 200):
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
    requests.get(url=url1, verify=False, headers=headers)  # 求稳
    re_data = requests.get(url=url2, verify=False, headers=headers)
    while re_data.status_code != 200:
        requests.get(url=url1, verify=False, headers=headers)
        sleep(1)
        re_data = requests.get(url=url2, verify=False, headers=headers)
        print(re_data.status_code)
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
            if(jsons[wnp].find(j) != -1):
                lists.append(jsons['id'])
                print(jsons[wnp])
                break
        if(q):
            continue
        # 黑名单
        p = True
        for k in black_list:
            if(jsons[bnp].find(k) != -1):
                p = False
                break
        if(p):
            lists.append(jsons['id'])
            print(jsons[bnp])

    # 抢课
    url3 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!batchOperator.action?profileId=" + profileid
    while True:
        for i in lists:
            postdata = {"optype": "true",
                        "operator0": str(i) + ":true:0"}
            rew = requests.session().post(url=url3, verify=False,
                                          data=postdata, headers=headers)
            if rew.text.find('失败') < 0:
                print("成功")


def main():
    config_info = get_config()
    cookies = get_cookie(
        config_info["student_id"], config_info["password"], config_info["semester_id"])
    grap_class(cookies)


# //2021级1616
# //2020级1613
# //2019级1611
# //2022/3/29
if __name__ == "__main__":
    main()
