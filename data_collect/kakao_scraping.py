# 페이지 소스 보기 : ctrl + shift + i (Mac) / f12 (Windows)
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
import polars as pl
import re
import time

# 1. csv 에서 네이버 맛집 리스트 가져오기
today = datetime.now().strftime("%Y%m%d")
data = pl.read_csv(f'naver_{today}.csv', columns=[0, 1])

# 2. 각 맛집 별로 정보 가져오기
options = Options()
options.add_experimental_option("detach", True)
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

spot_list = []
for spot in data.iter_rows():
    new = {'spot_cd': spot[0], 'spot_nm': spot[1]}
    try:
        url = f"https://map.kakao.com/?q={spot[1]}"
        driver.get(url)
        driver.implicitly_wait(time_to_wait=3)
        # 검색 결과의 첫번째 가게 클릭
        driver.find_element(By.CSS_SELECTOR, '#info\.search\.place\.list > li > div.info_item > div.contact.clickArea > a.moreview').send_keys(Keys.ENTER)
        # 새로 생긴 탭으로 이동
        driver.switch_to.window(driver.window_handles[-1])
        # 카카오 맛집 링크 추출
        new['kakao_url'] = driver.current_url
        # 평점, 리뷰 수, 리뷰 추출
        details = driver.find_element(By.CLASS_NAME, 'place_details')
        try:
            new['rating_amt'] = float(details.find_element(By.CSS_SELECTOR,'div > div > a:nth-child(3) > span.color_b').text)
            review_cnt = details.find_element(By.CSS_SELECTOR, 'div > div > a:nth-child(3) > span.color_g').text
            new['review_cnt'] = int(re.findall(r'\d+', review_cnt)[0])
            reviews = driver.find_elements(By.CLASS_NAME, 'txt_comment')
            new['review_list'] = [r.text for r in reviews]
        except:
            new['rating_amt'], new['review_cnt'], new['review_list'] = -1, -1, -1
        # 블로그 포스팅 수 추출
        try:
            new['blog_cnt'] = int(details.find_element(By.CSS_SELECTOR, 'div > div > a:nth-child(5) > span').text)
        except:
            new['blog_cnt'] = -1
        # 메뉴 추출
        try:
            menu_dict = dict()
            menu_list = driver.find_element(By.CLASS_NAME, 'list_menu')
            menus = menu_list.find_elements(By.CLASS_NAME, 'loss_word')
            menus_price = menu_list.find_elements(By.CLASS_NAME, 'price_menu')
            for a, b in zip(menus, menus_price):
                menu_dict[a.text] = b.text
            new['menu_dict'] = menu_dict
        except:
            new['menu_dict'] = -1
        driver.close()
        time.sleep(0.3)
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e1:
        new['kakao_url'] = -1
        driver.switch_to.window(driver.window_handles[0]);
        pass
    print(new)
    spot_list.append(new)
driver.close()

# 3. 카카오 맛집 데이터 저장
with open(f'kakao_{today}.json', 'w', encoding='utf-8') as f:
    json.dump({today: spot_list}, f, ensure_ascii=False, indent=4)