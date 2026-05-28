
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

def get_category_list(browser: webdriver.Chrome) -> list[dict[str,object]]:
    # ul_element = browser.find_element(By.CSS_SELECTOR, "ul[class^='category_wrap']")

    def parse_category_item(element:WebElement) -> dict[str,object]:
        """
            解析分类项

            目前是a标签

            <a 
            class="f-14 td-n gray87 ml-6 mr-6 ellipsis" 
            style="transition:color 0.2s ease-in-out" 
            href="https://s.1688.com/selloffer/offer_search.htm?charset=utf8&amp;keywords=办公文化" 
            target="_blank" 
            data-spm="dL2">
                办公文化
            </a>
        """

        name = element.text.strip()
        url = element.get_attribute("href")
        return {
            "name": name,
            "url": url,
            'source': element
            
        }
    
    
    def parse_category_row(li_element:WebElement) -> list[dict[str,object]]:
        """
           解析分类行
           一个 li 表示一行 包含 3 个a 标签分类（后续可能会变化 不确定）

        """
        a_elements = li_element.find_elements(By.XPATH, "./a")

        if len(a_elements) > 0:
            return [parse_category_item(a) for a in a_elements]

        return []

    try:
       # 等待处理
       ul_element = WebDriverWait(browser,10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul[class^='category_wrap']"))
        )

    except:
        print("获取分类列表失败！")
        return []
    
    li_elements = ul_element.find_elements(By.XPATH, "./li")

    if  len(li_elements) == 0:
        print("没有找到分类列表项！")

    category_list = []

    for li in li_elements:
        category_list.extend(parse_category_row(li))

    return category_list

"""
    偷懒找个大概的规律提炼的模板
    根据委托解析详细元素的函数

    
"""
def parse_template(root_element: WebElement, row_selector:str , last_element_selector:str,last_element_handle) -> str:

    row_elements = root_element.find_elements(By.CSS_SELECTOR,row_selector) 

    if len(row_elements) == 0:
        print(f"没有找到行元素！选择器: {row_selector}")
        return ''
    
    result = ''

    for row_element in row_elements:
        last_row_element = row_element.find_elements(By.CSS_SELECTOR,last_element_selector)

        if len(last_row_element) == 0:
            print(f"没有找到最后元素！选择器: {last_element_selector}")
            continue

        result = last_element_handle(row_element)

        if result is None:
            print(f"处理最后元素失败！选择器: {last_element_selector}")
        break
        
    return result

def parse_offer_title(offer_row_element: WebElement) -> str:
    return parse_template(offer_row_element,'div.offer-title-row', 'div.title-text', lambda e: e.text.strip())

def parse_offer_img(offer_row_element: WebElement) -> str:
    return parse_template(
        offer_row_element,
        'div.offer-img-wrapper',
        'div.offer-img-inner',
        lambda i: i.find_element(By.CSS_SELECTOR,'img').get_attribute('src')
    )

def parse_offer_desc(offer_row_element: WebElement) -> str:
    return parse_template(offer_row_element,'div.offer-desc-row','div.offer-desc-item div.desc-text',lambda e: e.text.strip())

def parse_offer_price(offer_row_element: WebElement) -> str:
    return parse_template(
        offer_row_element,
        'div.offer-price-row',
        'div.price-item',
        lambda e: f"{ e.find_element(By.CSS_SELECTOR,'div.text-main').text.strip()} { e.find_element(By.CSS_SELECTOR,'div.price-units').text.strip() }"
    )

def parse_offer_list(browser: webdriver.Chrome) -> list[dict[str,object]]:

    offerlist_element = browser.find_elements(By.CSS_SELECTOR,'div.space-common-offerlist')
    
    if len(offerlist_element) == 0:
        print("没有找到报价列表元素！")
    
    offerlist_element = offerlist_element[0]

    feeds_wrapper_element = offerlist_element.find_elements(By.CSS_SELECTOR,'div.feeds-wrapper')
    
    if len(feeds_wrapper_element) == 0:
        print("没有找到报价列表容器元素！")
    
    feeds_wrapper_element = feeds_wrapper_element[0]

    # 原本使用a标签获取所有 但是发现如果要包含推荐位的物品的话可能会再包一层div 
    offerlist_item_elements = feeds_wrapper_element.find_elements(By.XPATH,"./*[self::div or self::a][contains(@class,'search-offer-item')]")
    
    # 没有处理广告位
    return [ 
        {
            'title': parse_offer_title(offer),
            'img': parse_offer_img(offer),
            'desc': parse_offer_desc(offer),
            'price': parse_offer_price(offer),
        } 
        for offer in offerlist_item_elements
    ]
