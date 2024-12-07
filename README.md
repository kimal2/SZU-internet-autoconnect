# SZU自动联网

利用Windows自动任务实现登录系统时自动联网

宿舍区插网线上网或WiFi都可以用

本方法需要**Python**



## 1.安装Python，然后安装requests

​	1.安装Python，这里不做教程，自行百度

​	2.安装完成后，打开CMD输入以下命令来安装requests库

```
	pip install requests
```



## 2.编辑Python代码

​	1.复制以下代码，或者下载上传的.py文件

```
import requests

def check_network_connection():
    try:
        response = requests.head("http://www.baidu.com", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

user_account  = ""     #引号里输入你的卡号
user_password = ""     #引号里输入你的密码

if check_network_connection():
    exit()
else:
    response = requests.get(f"http://172.30.255.42:801/eportal/portal/login/?user_account={user_account}&user_password={user_password}")
    print(response.text)
```

​	2.建新文本粘贴此代码，按提示输入你的卡号和密码，保存后退出，然后将文件扩展名改为.py，把这个文件放到一个不被打扰的地方



## 3.Windows自动任务

​	1.Windows搜索框搜索`任务计划程序`

​	![](img/1.png “步骤1”)

​	2.打开后在右边选择`创建任务`，在弹出的新窗口选`触发器`下面有个`建新`，开始任务选`启动时`延迟改为`3秒`（先选30秒再手动改为3秒，这里延迟时间按你的电脑来，电脑慢的可以选择久一点）然后确定。然后再次建新，这次开始任务选择`工作站解锁时`,延迟同上

​	![](img/2.png “步骤2”)

​	3.第二步完成后选触发器右边的`操作`,新窗口的操作选择`启动程序`，`程序或脚本`那里找到你安装Python的目录选择`pythonw.exe`这样运行不会有弹窗，接下来是`添加参数`，里面填你的.py文件的地址，注意这个要把文件名也加上去，如

```
C:\Users\username\Downloads\1.py
```

然后是`起始于`，这个很简单直接把上面的“\文件.py”删了粘贴进去就行，如

```
C:\Users\username\Downloads
```

​	![](img/3.png “步骤3”)	

​	4.条件里的电源选项选择`唤醒计算机运行此任务`



## 4.大功告成



这破校园网每次启动都掉线，迫不得已搞了个这个，感谢AI提供的大部分代码，谢谢KIMI、豆包等AI的支持，你们辛苦了❤️，有问题可以问AI因为我也不会：）

还有感谢[[抓包分析,一条Linux命令实现路由器自动登录深大校园网认证(Drcom Pt版)_172.30.255.42-CSDN博客](https://blog.csdn.net/TeleostNaCl/article/details/124553119)]的URL

