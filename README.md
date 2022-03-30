# xsyu_electives_script
西安石油大学抢课脚本

```json 
{
    "student_id": "", //填上你的学号
    "password": "", //填上你的密码
    "semester_id": "162", //不要动
    "select_id": "1", //暂时无用
    "white_list": [""], //白名单，方括号内填上你想抢的课的课程名（包含部分文字就行）或者老师名，例如["定向","鉴赏"]
    "wnp": "name", //如果上面填的是课程名，就不用改，如果填的是老师名就把name改为teachers
    "black_list": ["A", "B"], //黑名单,跟上面白名单刚好相反，要使用黑名单，白名单就不要填东西
    "bnp": "name" //如果黑名单写的是老师名字，这里就改为teachers
}
