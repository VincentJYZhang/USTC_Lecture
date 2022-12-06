"""
@author: zhang
@date: 2021.04.21
"""

import requests
from requests._internal_utils import to_native_string
from requests.compat import is_py3
import user_config
from urllib import parse

from retry import retry


# USTC的教务网有个问题，他的重定向编码不是utf8，requests库自动解码会出问题
# 这里将requests库里的重定向函数hook出来重写
def get_redirect_target(self, resp):
    """hook requests.Session.get_redirect_target method"""
    if resp.is_redirect:
        location = resp.headers['location']
        if is_py3:
            location = location.encode('latin1')
        encoding = resp.encoding if resp.encoding else 'utf-8'
        return to_native_string(location, encoding)
    return None


def patch():
    requests.Session.get_redirect_target = get_redirect_target



@retry(tries=3)
def getSessionByAuth(stu_id, pwd):
    """get student id by password
    """
    
    headers = {
        "Connection":"keep-alive",
        "Cache-Control":"max-age=0",
        "sec-ch-ua":'" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
        "sec-ch-ua-mobile":"?0",
        "Origin":"https://passport.ustc.edu.cn",
        "Upgrade-Insecure-Requests":"1",
        "DNT":"1",
        "Content-Type":"application/x-www-form-urlencoded",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.42",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Sec-Fetch-Site":"same-origin",
        "Sec-Fetch-Mode":"navigate",
        "Sec-Fetch-User":"?1",
        "Sec-Fetch-Dest":"document",
        "Referer":"https://passport.ustc.edu.cn"
    }

    url_raw = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fyjs%2Eustc%2Eedu%2Ecn%2Fdefault%2Easp"
    
    url = "https://passport.ustc.edu.cn/login"

    s = requests.Session()

    r = s.get(url_raw, headers=headers)

    import re

    pattern = r'name="CAS_LT" value=".+?">'
    index = re.search(pattern, r.text).span()

    CAS_LT = r.text[index[0]+21:index[1]-2]

    form_data = """model=uplogin.jsp&CAS_LT={}&service=http%3A%2F%2Fyjs.ustc.edu.cn%2Fdefault.asp&warn=&showCode=&username={}&password={}&button=""".format(CAS_LT, stu_id, pwd)

    r = s.post(url, headers=headers, data=form_data)

    if r.status_code != 200:
        raise Exception('status code: ' + r.status_code)

    return s


@retry(tries=3)
def selectLecture(session_, lecture_id):

    url = 'http://yjs.ustc.edu.cn/bgzy/m_bgxk_up.asp'

    headers = {
        "Proxy-Connection":"keep-alive",
        "Cache-Control":"max-age=0",
        "Upgrade-Insecure-Requests":"1",
        "Origin":"http://yjs.ustc.edu.cn",
        "Content-Type":"application/x-www-form-urlencoded",
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Referer":"http://yjs.ustc.edu.cn/bgzy/m_bgxk_up.asp",
        "Accept-Language":"zh-CN,zh;q=0.9"
    }

    patch()

    form_data = {
        "selectxh": int(lecture_id),
        "select": "true"
    }

    form_data = parse.urlencode(form_data)

    r = session_.post(url, headers = headers, data = form_data)

    r.encoding = "gb2312"

    if r.status_code != 200:
        raise Exception('status code: ' + r.status_code)

    return True





import tkinter
import tkinter.messagebox
from tkinter import *
import user_config


stu_id = user_config.USER_NAME
pwd = user_config.USER_PWD
lec_id = user_config.LEC_ID
top = tkinter.Tk()


def finish():
    #get info
    stu_id = stu_id_entry.get()
    pwd = pwd_entry.get()
    lec_id = lec_id_entry.get()

    #save last info
    config_file = open("user_config.py","w")
    config_file.write("USER_NAME = '"+ stu_id +"'\n")
    config_file.write("USER_PWD = '"+ pwd +"'\n")
    config_file.write("LEC_ID = '"+ lec_id +"'\n")

    #send request
    session_ = getSessionByAuth(stu_id, pwd)
    result_flag = selectLecture(session_,lec_id)
    end_word = """选课请求发送成功，请至官网检查是否成功。\n如果发现失败，可能原因如下：
    1. 用户名或密码不正确；
    2. 讲座编号输入有误；
    3. 其他未知玄学原因。"""
    error_word = """选课失败，请检查网络。"""
    if result_flag:
        print(end_word)
    else:
        print(error_word)
    tkinter.messagebox.showinfo("",end_word)




def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    print(size)
    root.geometry(size)
    root.update()
    print(root.winfo_x())


center_window(top, 150, 200)
top.resizable(width=0, height=0)
top.iconbitmap('assets\logo2.ico')
top.configure(bg = "SkyBlue")
top.title(" ")

stu_id_label = Label(top, text="学号",bg = "SkyBlue",font=("楷体", 10))
stu_id_label.pack()
stu_id_entry = Entry(top, bd =10,highlightcolor='green',highlightthickness=1)
stu_id_entry.insert(0,stu_id)
stu_id_entry.pack()

pwd_label = Label(top, text="密码",bg = "SkyBlue",font=("楷体", 10))
pwd_label.pack( )
pwd_entry = Entry(top, bd =10,show="*",highlightcolor='green',highlightthickness=1)
pwd_entry.insert(0,pwd)
pwd_entry.pack()

lec_id_label = Label(top, text="课程编号",bg = "SkyBlue",font=("楷体", 10))
lec_id_label.pack( )
lec_id_entry = Entry(top, bd =10, highlightcolor='green',highlightthickness=1)
lec_id_entry.insert(0,lec_id)
lec_id_entry.pack()
button = tkinter.Button(top, text ="确认", command = finish,bg = "SkyBlue",font=("楷体", 10))
button.pack(side=LEFT,ipadx = 20)


button = tkinter.Button(top, text ="退出", command = top.destroy,bg = "SkyBlue",font=("楷体", 10))
button.pack(side=RIGHT,ipadx = 20)



if __name__ == "__main__":

    print('=========学术报告选课脚本=========\n')
    top.mainloop()

    
