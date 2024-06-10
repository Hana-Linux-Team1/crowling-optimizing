import requests
from bs4 import BeautifulSoup
import csv
import time

# 시작 시간 기록
start_time = time.time()

# 파일명 설정
csv_file = 'daangn_articles1.csv'

# CSV 파일을 생성하고 헤더 작성
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['ID', 'Title', 'Price', 'Description'])

# 수집된 데이터 수
collected_data_count = 0
article_id = 1

while collected_data_count < 100:
    url = f"https://www.daangn.com/articles/{article_id}"
    
    try:
        # 웹 페이지 가져오기
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # 페이지가 존재하지 않으면 예외 발생

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')

        # article-title, article-price, article-description 찾기
        title_tag = soup.find('h1', id='article-title')
        price_tag = soup.find('p', id='article-price')
        description_tag = soup.find('div', id='article-detail')

        # 텍스트 추출
        title = title_tag.get_text(strip=True) if title_tag else None
        price = price_tag.get_text(strip=True) if price_tag else None
        description = description_tag.get_text(strip=True) if description_tag else None

        # 유효한 데이터가 있는 경우에만 CSV 파일에 추가
        if title and price and description:
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([article_id, title, price, description])
            collected_data_count += 1
            print(f"Article {article_id} has been written to {csv_file}")

    except requests.HTTPError as e:
        # 페이지가 존재하지 않으면 다음으로 넘어감
        print(f"[{response.status_code}] Article {article_id} does not exist. Skipping...")
    except Exception as e:
        print(f"An error occurred while fetching article {article_id}: {e}")

    article_id += 1

# 종료 시간 기록
end_time = time.time()
elapsed_time = end_time - start_time  # 소요 시간 계산

print(f"Data has been written to {csv_file}")
print(f"Elapsed time: {elapsed_time:.2f} seconds")

#279.29초 소요