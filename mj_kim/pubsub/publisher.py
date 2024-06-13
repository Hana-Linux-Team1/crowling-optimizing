import redis
import json


def producer_task(urls):
    # Redis 서버에 연결
    r = redis.Redis()
    for url in urls:
        # 크롤링할 URL을 JSON 형태로 변환하여 Redis의 'carrot_tasks' 리스트에 추가
        task = json.dumps({'url': url})
        r.lpush('carrot_tasks', task)
        print(f'Task added: {task}')


if __name__ == '__main__':
    # 당근 마켓 게시글 URL
    url = 'https://www.daangn.com/articles/'

    # 당근 마켓 게시글 번호
    index = 783227594

    # 크롤링할 URL 리스트 초기화
    urls_to_scrape = []

    # 100개의 게시글 URL을 크롤링할 URL 리스트에 추가
    for i in range(0, 100):
        tmp_index = index - i
        article_url = f'{url}{tmp_index}'
        urls_to_scrape.append(article_url)

    producer_task(urls_to_scrape)
