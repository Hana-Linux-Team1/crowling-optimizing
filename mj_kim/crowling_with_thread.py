import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def fetch_article_data(article_id):
    url = f"https://www.daangn.com/articles/{article_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_tag = soup.find('h1', id='article-title')
        price_tag = soup.find('p', id='article-price')
        description_tag = soup.find('div', id='article-detail')
        
        title = title_tag.get_text(strip=True) if title_tag else None
        price = price_tag.get_text(strip=True) if price_tag else None
        description = description_tag.get_text(strip=True) if description_tag else None
        
        if title and price and description:
            return article_id, title, price, description
        else:
            return None

    except requests.HTTPError as e:
        print(f"[{response.status_code}] Article {article_id} does not exist. Skipping...")
        return None
    except Exception as e:
        print(f"An error occurred while fetching article {article_id}: {e}")
        return None

def main():
    start_time = time.time()  # 시작 시간 기록
    
    csv_file = 'daangn_articles2.csv'
    
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Title', 'Price', 'Description'])

    article_id = 1
    collected_data_count = 0
    max_workers = 10
    futures = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while collected_data_count < 100:
            future = executor.submit(fetch_article_data, article_id)
            futures.append(future)
            article_id += 1

            # 완료된 작업 처리
            if len(futures) >= max_workers:
                for future in as_completed(futures):
                    try:
                        article_data = future.result()
                        if article_data:
                            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                                writer = csv.writer(file)
                                writer.writerow(article_data)
                            collected_data_count += 1
                            print(f"Article {article_data[0]} has been written to {csv_file}")

                            if collected_data_count >= 100:
                                break
                    except Exception as e:
                        print(f"An error occurred: {e}")

                futures = []

    end_time = time.time()  # 종료 시간 기록
    elapsed_time = end_time - start_time  # 소요 시간 계산

    print(f"Data has been written to {csv_file}")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()

#45.71초 소요 -> worker 10개
#22.58초 소요 -> worker 20개

# 7.35초 소요 -> worker 100개