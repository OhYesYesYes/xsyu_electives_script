import json
import re
import time
from time import sleep
import requests
from soupsieve import select
from xsyu_login import get_cookie, waiting, do_not_access_fast
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    flag = True
    while flag:
        try:
            re_id = requests.get(url=url_for_id, verify=False, headers=headers,timeout=(5,10))
            if "是 否 选 课" in re_id.text:  
                id_str = re_id.text.split("confirmElection(")
                profileid = id_str[1][:4]
                flag = False
                return profileid
            sleep(2)
        except:
            pass


def grap_class(cookies):
    headers = {"Cookie": cookies}
    profileid = get_profileid(cookies)
    # 循环到选课时间
    url1 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id=" + profileid
    url2 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!data.action?profileId=" + profileid
    flag = True
    while flag:
        try:
            requests.get(url=url1, verify=False, headers=headers)
            re_data = requests.get(url=url2, headers=headers)
            print("正在运行中...状态码: ", re_data.status_code)
            if re_data.status_code==200:
                break
            sleep(1)
        except:
            pass
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
                if (jsons[wnp].find(j) != -1):
                    q = True
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
        try:
            while_flag = 0
            if num_flag == 5:
                num_flag = 0
            # 定向，15533
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
            num_flag += 1
            while_flag += 1
        except:
            pass

def main():
    try:
        config_info = get_config()
    except:
        print("没有找到config.json配置文件，请将配置文件放在同一目录!")
        print("也有可能你的config.json文件配置错误，请检查！注意在[]中添加内容时需要添加引号以及使用utf-8")
        os.system("pause")
        return
    cookies = get_cookie(config_info["student_id"], config_info["password"])
    grap_class(cookies)

if __name__ == "__main__":
    main()
