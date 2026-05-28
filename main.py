import json
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import Parser.private1688Parser as parser
import time

# 暂时写死方便测试特点版本
service = webdriver.ChromeService(executable_path=r"C:\Dev\python_workspace\webdriver\Chrome\148.0.7778.179\chromedriver.exe")

options = webdriver.ChromeOptions()

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
options.add_argument(f"User-Agent={user_agent}")


options.add_argument("--disable-blink-features=AutomationControlled")  # 核心：隐藏webdriver
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 去掉自动化提示
options.add_experimental_option("useAutomationExtension", False)  # 禁用自动化扩展

options.add_argument("--start-maximized")  # 窗口最大化
options.add_argument("--no-sandbox")  # 关闭沙盒
options.add_argument("--disable-dev-shm-usage")  
options.add_argument("--disable-extensions")  # 禁用扩展
options.add_argument("--disable-plugins")  # 禁用插件

driver_instance = webdriver.Chrome(service=service,options=options)

# driver_instance.execute_script("""
#         Object.defineProperty(navigator, 'webdriver', {
#             get: () => undefined
#         })
#     """)
# driver_instance.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
#       'source': 'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'
#     })

driver_instance.get("https://www.1688.com/")

def check_and_close_verification() -> bool:
    # 如果检测到验证码元素存在，则返回True，否则返回False
    # 这里的XPath需要根据实际页面结构进行调整
    # 改成Cookies 这里赞数不用验证码，不太好过
    return False

def try_setup_1688_cookies(browser: webdriver.Chrome):

    def read_cookies_from_file() -> list[dict[str,object]]:

        # 读取文件
        try:
            # 暂时写死方便测试
            # TODO:: 之后可以改成参数传入
            with open(r"C:\Dev\python_workspace\1688State.json","r",encoding="utf-8") as f:
                cookiesJson = f.read()
        except:
            print("读取 cookies 文件失败！")
            return []

        # 解析 JSON
        try:
           cookies :list[dict]= json.loads(cookiesJson)
           return cookies

        except:
            print("解析 cookies 文件失败！")
            return []
    
    cookies = read_cookies_from_file()

    for cookie in cookies:
        try:
            driver_instance.add_cookie(cookie)
        except:
            print(f"添加 cookie 失败: {cookie['name']}")
            return False

    return len(cookies) > 0;        

# if not check_and_close_verification():
#     print("验证码出现了！")

# is_ok = input("wait for log in and press Enter to continue...")

# state_dump_file_path = './1688State.json'

# if is_ok == 'y':
#     loginState = driver_instance.get_cookies()
#     with open(state_dump_file_path,'w',encoding='utf-8') as f:
#         json.dump(loginState,f)
# else:
#     with open(state_dump_file_path,'r',encoding='utf-8') as f:
#         loginState = json.load(f)
#         for cookie in loginState:
#             try:
#                 driver_instance.add_cookie(cookie)
#             except:
#                 print(f"添加 cookie 失败: {cookie['name']}")

try_setup_1688_cookies(driver_instance) 

# 刷新下浏览器
driver_instance.refresh()

# 获取分类信息
category_list = parser.get_category_list(driver_instance)

if len(category_list) == 0:
    print("没有获取到分类列表！")

for category in category_list:
    print(f"分类名称: {category['name']}, 分类链接: {category['url']}")

# 随机选择一个分类 方便测试
selected_category = random.choice(category_list)

print(f"随机选择的分类: {selected_category['name']}")

# 获取分类详情链接
category_detail_url = str(selected_category['url'])

# 模拟点击应该更好？ 但是没看出差别来，如果遇到频率限制这里改成点击较好？
driver_instance.get(category_detail_url)

offer_list = parser.parse_offer_list(driver_instance)

for offer in offer_list:
    print(f"商品名称: {offer}")

input("Press Enter to close the browser...")


