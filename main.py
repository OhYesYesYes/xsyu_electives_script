import json
import re
from time import sleep
import requests
from xsyu_login import get_cookie


def get_config(path="./config.json"):
    info_dict = {}
    with open(path, "r", encoding="utf-8") as f:
        info_dict = json.load(f)
    f.close()
    return info_dict

def grap_class(profileid,cookies):
    url1 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!data.action?profileId=" + profileid
    url2 = "http://jwxt.xsyu.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id=" + profileid
    headers = {"Cookie": cookies}
    # res = requests.get(url=url2, verify=False, headers=headers)
    ret = requests.get(url=url1, verify=False, headers=headers)
    print(ret.status_code)
    while ret.status_code != 200:
        # res = requests.get(url=url2, verify=False, headers=headers)
        sleep(1)
        ret = requests.get(url=url1, verify=False, headers=headers)
        print(ret.status_code)
    text = ret.text[22:-1]
    list = text.split(",{id")
    # print(list)
    lists = []
    for i in list:
        i = "{'id'" + i
        i = i.replace("'", "\"")
        i = re.sub(r',(.*?):', r',"\1":', i)
        i = i[:i.index(',"remark')] + "}"
        jsons = json.loads(i)
        if (jsons['name'].find('定向') != -1 or jsons['name'].find('世界') != -1 or jsons['name'].find('婚') != -1 or jsons[
            'name'].find('中国史') != -1 or jsons['name'].find('心理') != -1):
            lists.append(jsons['id'])
            print(jsons['name'])
    print(lists)

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
    profileid = config_info["profileid"]
    cookies = get_cookie(config_info["student_id"], config_info["password"], config_info["semester_id"])
    grap_class(profileid,cookies)



# //2021级1616
# //2020级1613
# //2019级1611
# //2022/3/29
if __name__ == "__main__":
    main()
