import redis
import json
import time
from multiprocessing import Process

# 프로세스 수
MAX_PROCESSES = 3

def producer_task(urls):
    # Redis 서버에 연결
    r = redis.Redis()
    for url in urls:
        # 크롤링할 URL을 JSON 형태로 변환하여 Redis의 'carrot_tasks' 리스트에 추가
        task = json.dumps({'url': url})
        r.lpush('carrot_tasks', task)
        print(f'Task added: {task}')

def manage_consumers():
    from consumer import consumer_task  # consumer.py에 있는 consumer_task 함수 가져오기

    # 프로세스 관리 리스트
    processes = []

    while True:
        # 프로세스가 MAX_PROCESSES보다 작으면 새로운 프로세스를 시작
        if len(processes) < MAX_PROCESSES:
            # 소비자 프로세스 시작
            p = Process(target=consumer_task)
            p.start()

            # 프로세스 관리 리스트에 추가
            processes.append(p)
            print(f'Started process {p.pid}')
        else:
            # 프로세스가 MAX_PROCESSES보다 크면 종료된 프로세스를 제거
            for p in processes:
                # 프로세스가 종료되었으면 제거
                if not p.is_alive():
                    processes.remove(p)
                    print(f'Terminated process {p.pid}')
        time.sleep(0.1)

    # 모든 프로세스가 종료될 때까지 대기
    for p in processes:
        p.join()
        print(f'Joined process {p.pid}')

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

    # 프로듀서 작업 수행
    producer_task(urls_to_scrape)

    # 소비자 프로세스 관리 시작
    manage_consumers()
