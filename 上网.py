import requests
import json
import os
import time
import re
from cryptography.fernet import Fernet  # 引入加密库

# ================= 配置区域 =================
CONFIG_FILE = "config.json"
KEY_FILE = ".secret.key"  # 存放解密密钥的文件

LOGIN_URL = "http://172.30.255.42:801/eportal/portal/login"
CHECK_URL = "https://www.baidu.com"  # 百度检测

# 账号前缀
ACCOUNT_PREFIX = ",0,"


# ===========================================

def load_or_generate_key():
    """
    加载或生成加密密钥
    如果密钥文件不存在，生成一个新的并保存。
    """
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        # 生成新密钥
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)

        # (可选) 在Windows下尝试将密钥文件设为隐藏
        if os.name == 'nt':
            try:
                os.system(f"attrib +h {KEY_FILE}")
            except:
                pass
        return key


def get_cipher():
    """获取加密套件实例"""
    key = load_or_generate_key()
    return Fernet(key)


def ask_user_input():
    print("\n>>> 进入账号设置模式 (加密存储) <<<")
    while True:
        account = input("请输入账号：").strip()
        if account: break
        print("账号不能为空！")

    while True:
        password = input("请输入密码：").strip()
        if password: break
        print("密码不能为空！")

    try:
        # === 加密过程 ===
        cipher = get_cipher()
        # Fernet只能加密bytes，需要先encode
        enc_account = cipher.encrypt(account.encode("utf-8")).decode("utf-8")
        enc_password = cipher.encrypt(password.encode("utf-8")).decode("utf-8")

        data = {
            "account": enc_account,
            "password": enc_password,
            "encrypted": True  # 标记这是加密过的
        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ 账号密码已加密并保存到本地。")
        return account, password
    except Exception as e:
        print(f"配置文件写入失败: {e}")
        return account, password


def get_account(force_input=False):
    """
    获取账号密码：读取文件 -> 解密
    """
    if not force_input and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)

            enc_acc = config.get("account", "").strip()
            enc_pwd = config.get("password", "").strip()

            if enc_acc and enc_pwd:
                # === 解密过程 ===
                cipher = get_cipher()
                # 尝试解密，如果密钥不对或文件损坏，会抛出异常
                dec_acc = cipher.decrypt(enc_acc.encode("utf-8")).decode("utf-8")
                dec_pwd = cipher.decrypt(enc_pwd.encode("utf-8")).decode("utf-8")
                return dec_acc, dec_pwd

        except Exception:
            # 包含：文件格式错误、解密失败(InvalidToken)、Key丢失等所有情况
            print("⚠️ 配置文件无效或解密失败（可能是密钥变更），需重新输入。")
            pass

    return ask_user_input()


def check_internet_access():
    """检查是否能访问百度"""
    try:
        resp = requests.get(CHECK_URL, timeout=3)
        return resp.status_code == 200
    except:
        return False


def parse_server_msg(text):
    """从JSONP中提取核心信息"""
    try:
        match = re.search(r'"msg":"(.*?)"', text)
        if match: return match.group(1)
        match_res = re.search(r'"result":(\d+)', text)
        if match_res: return f"返回代码 {match_res.group(1)}"
    except:
        pass
    return "未知响应内容"


def login_process():
    # 获取解密后的账号密码
    account, password = get_account(force_input=False)

    # 自动补全前缀
    final_account = account
    if ACCOUNT_PREFIX and not account.startswith(ACCOUNT_PREFIX):
        final_account = ACCOUNT_PREFIX + account
        print(f"提示：账号前缀校正完毕。")

    max_retries = 5
    retry_count = 0

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "http://172.30.255.42:801/"
        })

        while retry_count < max_retries:
            try:
                print(f"正在尝试登录... (第 {retry_count + 1}/{max_retries} 次)")

                params = {
                    "callback": "dr1005",
                    "login_method": "1",
                    "user_account": final_account,
                    "user_password": password,
                    "wlan_user_ip": "",
                    "wlan_user_mac": "000000000000",
                    "wlan_ac_ip": "",
                    "jsVersion": "4.1.3",
                    "terminal_type": "1",
                    "lang": "zh-cn",
                    "v": "1139"
                }

                response = session.get(LOGIN_URL, params=params, timeout=5)
                response.encoding = response.apparent_encoding
                res_text = response.text

                clean_msg = parse_server_msg(res_text)
                print(f"服务器反馈: [{clean_msg}]")

                # 判定成功
                if ('dr1005' in res_text and '"result":1' in res_text) or \
                        ("认证成功" in res_text) or \
                        ("已经在线" in res_text):
                    print("🚀 登录成功！")
                    return True

                # 判定拥堵
                if response.status_code in [503, 502, 504]:
                    print(f"⚠️ 服务器繁忙 (HTTP {response.status_code})，稍后重试...")

                # 判定账号错误
                elif '"result":0' in res_text and any(k in res_text for k in ["密码", "账号", "不存在", "error"]):
                    print("\n❌ 严重错误：账号或密码无效！")
                    # 这里的True会触发重新输入，并自动重新加密保存
                    account, password = get_account(force_input=True)
                    final_account = ACCOUNT_PREFIX + account if ACCOUNT_PREFIX else account
                    retry_count = 0
                    print("🔄 已更新信息，立即重试...")
                    continue

                else:
                    print("⚠️ 未知状态，准备重试...")

            except requests.exceptions.RequestException as e:
                print(f"⚠️ 网络连接异常: {e}")

            retry_count += 1
            if retry_count < max_retries:
                time.sleep(2)

        print("\n❌ 已达到最大重试次数，登录失败。")
        return False


def main():
    print("=== 校园网自动登录脚本 ===")

    if check_internet_access():
        print("✅ 网络已连接 (百度可达)，无需执行登录。")
        print("程序将在 2 秒后退出...")
        time.sleep(2)
        return

    if login_process():
        time.sleep(1)
        if check_internet_access():
            print("✅✅✅ 最终结果：网络已完全联通！")
            print("程序将在 2 秒后退出...")
            time.sleep(2)
        else:
            print("❌ 登录接口显示成功，但无法访问百度（可能欠费）。")
            print("程序将在 5 秒后退出...")
            time.sleep(5)
    else:
        print("❌ 登录失败，请检查网络或配置。")
        print("程序将在 5 秒后退出...")
        time.sleep(5)


if __name__ == "__main__":
    main()