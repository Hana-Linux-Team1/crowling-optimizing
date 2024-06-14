import redis
import json
import time
from multiprocessing import Process
import argparse
import sys

def producer_task(urls):
    # Redis 서버에 연결
    r = redis.Redis()
    for url in urls:
        # 크롤링할 URL을 JSON 형태로 변환하여 Redis의 'carrot_tasks' 리스트에 추가
        task = json.dumps({'url': url})
        r.lpush('carrot_tasks', task)
        print(f'Task added: {task}')


def manage_consumers(max_processes):
    from consumer import consumer_task  # consumer.py에 있는 consumer_task 함수 가져오기

    r = redis.Redis()

    # 프로세스 관리 리스트
    processes = []

    try:
        while True:
            current_length = r.llen('carrot_tasks')  # 레디스 큐의 길이를 계속 갱신
            print(f'Current length: {current_length}')
            # 새로운 프로세스 시작 조건
            while len(processes) < max_processes and current_length > 0:
                p = Process(target=consumer_task)
                p.start()
                processes.append(p)
                print(f'Started process {p.pid}')
                

            # 종료된 프로세스 청소
            processes = [p for p in processes if p.is_alive()]

            # 모든 프로세스가 종료되었고, 더 이상 처리할 작업이 없을 때 종료
            if current_length == 0:
                break

            time.sleep(1)  # CPU 사용률을 관리하기 위한 간단한 딜레이
        print("Processes")
        for p in processes:
            p.terminate()
    except KeyboardInterrupt:
        # Ctrl+C를 눌렀을 때 모든 프로세스 정리
        for p in processes:
            if p.is_alive():
                p.terminate()
            p.join()
        processes = []

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Carrot Market Scraping')
    parser.add_argument('--max_processes', type=int, default=3,
                        help='Maximum number of consumer processes to run')
    parser.add_argument('--index', type=int, default=783227594,
                        help='Starting index number for the articles')
    parser.add_argument('--count', type=int, default=100,
                        help='Number of articles to scrape')
    args = parser.parse_args()

    max_processes = args.max_processes
    start_index = args.index
    count = args.count

    # 당근 마켓 게시글 URL
    url = 'https://www.daangn.com/articles/'

    # 크롤링할 URL 리스트 초기화
    urls_to_scrape = []

    # 지정된 개수만큼 게시글 URL을 크롤링할 URL 리스트에 추가
    for i in range(count):
        tmp_index = start_index - i
        article_url = f'{url}{tmp_index}'
        urls_to_scrape.append(article_url)

    # 프로듀서 작업 수행
    producer_task(urls_to_scrape)

    # 소비자 프로세스 관리 시작
    manage_consumers(max_processes)
    print("hhi")
    sys.exit(0)
