import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
import time

# 시작 시간 기록
start_time = time.time()

# 파일명 설정
csv_file = 'daangn_articles3.csv'

async def fetch_article_data(session, article_id):
    url = f"https://www.daangn.com/articles/{article_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # 페이지가 존재하지 않으면 예외 발생
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')

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

    except aiohttp.ClientResponseError as e:
        print(f"[{e.status}] Article {article_id} does not exist. Skipping...")
        return None
    except Exception as e:
        print(f"An error occurred while fetching article {article_id}: {e}")
        return None

async def main():
    collected_data_count = 0
    article_id = 1

    async with aiohttp.ClientSession() as session:
        tasks = []
        while collected_data_count < 100:
            if len(tasks) >= 100:  # 10개의 요청을 동시에 실행
                done, pending = await asyncio.wait(tasks)
                for task in done:
                    article_data = task.result()
                    if article_data:
                        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow(article_data)
                        collected_data_count += 1
                        print(f"Article {article_data[0]} has been written to {csv_file}")
                tasks = [task for task in pending]
            tasks.append(asyncio.create_task(fetch_article_data(session, article_id)))
            article_id += 1

        # 남은 작업 처리
        done, pending = await asyncio.wait(tasks)
        for task in done:
            article_data = task.result()
            if article_data:
                with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(article_data)
                collected_data_count += 1
                print(f"Article {article_data[0]} has been written to {csv_file}")

if __name__ == "__main__":
    # CSV 파일을 생성하고 헤더 작성
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Title', 'Price', 'Description'])

    asyncio.run(main())

    # 종료 시간 기록
    end_time = time.time()
    elapsed_time = end_time - start_time  # 소요 시간 계산

    print(f"Data has been written to {csv_file}")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

# 33.94초 -> 10개
# 6.51초  -> 100개