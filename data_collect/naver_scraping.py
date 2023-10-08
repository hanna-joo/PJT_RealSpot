# pip install selenium
# pip install webdriver-manager
# pip install beautifulsoup4
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
from bs4 import BeautifulSoup
import re
import polars as pl


# css 찾을때 까지 최대 sec 초 대기
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


today = datetime.now().strftime("%Y%m%d")
url = 'https://map.naver.com/v5/search'
options = Options()
options.add_experimental_option("detach", True)
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

# 4. 페이지 소스 data 변수에 저장
data = BeautifulSoup(driver.page_source, 'html.parser').select('div.CHC5F')
driver.close()

# 5. 가게 이름, 평점, 리뷰 수 추출
columns = [('spot_cd', pl.Utf8), ('spot_nm', pl.Utf8), ('rating_amt', pl.Float64), ('review_cnt', pl.Int64)]
df = pl.DataFrame({}, schema=columns)
for i, x in enumerate(data):
    new = {'spot_cd': f'{today}{str(i+1).zfill(3)}'}
    # 가게 이름, 평점, 리뷰 수 추출
    new['spot_nm'] = x.select_one('span.TYaxT').get_text()
    raw = x.select_one('div.MVx6e').get_text() # 오늘 휴무별점4.29리뷰 999+
    rating_amt, review_cnt = re.findall(r'별점(\d+\.\d+|\d+)', raw), re.findall(r'리뷰 (\d*)', raw)
    new['rating_amt'] = float(rating_amt[0]) if rating_amt else float(-1)
    new['review_cnt'] = int(review_cnt[0]) if review_cnt else -1
    df = df.vstack(pl.DataFrame(new))

# 6. csv 형태로 로컬에 저장
df.write_csv(f'naver_{today}.csv')

