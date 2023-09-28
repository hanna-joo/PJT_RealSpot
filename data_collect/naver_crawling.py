# pip install selenium
# pip install webdriver-manager
# pip install beautifulsoup4
# 페이지 소스 보기 : ctrl + shift + i
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from time import sleep
from datetime import datetime


# css 찾을때 까지 최대 num초 대기
def time_wait(sec, selector):
    try:
        wait = WebDriverWait(driver, sec).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    except:
        print(selector, '태그를 찾기 못함')
        driver.quit()
    return wait


# frame 변경 메소드
def switch_frame(frame):
    driver.switch_to.default_content()  # frame 초기화
    driver.switch_to.frame(frame)  # frame 변경


# 페이지 스크롤 다운
def page_down(num):
    body = driver.find_element(By.CSS_SELECTOR, 'body')
    body.click()
    for i in range(num):
        body.send_keys(Keys.PAGE_DOWN)


options = Options()
options.add_experimental_option("detach", True)
url = 'https://map.naver.com/v5/search'
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.get(url)
keyword = '강남역 한식'  # 검색어


# 1. 선택자 찾을때까지 10초 대기
time_wait(10, 'div.input_box > input.input_search')

# 2. 검색어 입력 및 엔터
search = driver.find_element(By.CSS_SELECTOR, 'div.input_box > input.input_search')
search.send_keys(keyword)
search.send_keys(Keys.ENTER)
sleep(1)

# 3. frame 변경 및 스크롤 다운
switch_frame('searchIframe')
page_down(50)
sleep(3)

# 4. 페이지 소스 저장
today = datetime.now().strftime("%Y%m%d")
with open(f'naver_raw_{today}.html', 'w', encoding='utf-8') as file:
    file.write(driver.page_source)