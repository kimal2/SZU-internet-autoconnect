import requests

def check_network_connection():
    try:
        response = requests.head("http://www.baidu.com", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

user_account  = ""    #引号里输入你的卡号
user_password = ""     #引号里输入你的密码

if check_network_connection():
    exit()
else:
    response = requests.get(f"http://172.30.255.42:801/eportal/portal/login/?user_account={user_account}&user_password={user_password}")
    print(response.text)