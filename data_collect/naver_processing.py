# 데이터 정제
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

today = datetime.now().strftime("%Y%m%d")
with open(f'naver_raw_{today}.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# 가게 리스트만 추출
data = soup.select('div.CHC5F')

spot_list = []
for i, x in enumerate(data):
    new = dict()
    # 가게 이름, 별점, 리뷰 수 추출
    new['spot_name'] = x.select_one('span.TYaxT').get_text()
    raw = x.select_one('div.MVx6e').get_text() # 오늘 휴무별점4.29리뷰 999+
    star = re.findall(r'별점(\d+\.\d+|\d+)', raw)
    review = re.findall(r'리뷰 (\d*)', raw)
    new['rating_amt'] = float(star[0]) if star else -1
    new['review_cnt'] = int(review[0]) if review else -1
    spot_list.append(new)


with open(f'naver_process_{today}.json', 'w') as f:
    json.dump({today: spot_list}, f, ensure_ascii=False, indent=4)