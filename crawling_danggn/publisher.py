import redis
import json
import time
from multiprocessing import Process
import argparse
import sys
import os
import shutil
import datetime


def archive_screenshots(output_dir):
    # 현재 날짜와 시간 정보를 기반으로 타임스탬프 생성
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    # 압축 파일 이름 설정
    archive_name = f"{output_dir}_{timestamp}.zip"

    # screenshots 폴더를 압축
    shutil.make_archive(archive_name.replace('.zip', ''), 'zip', output_dir)
    print(f"Archived {output_dir} to {archive_name}")


def initialize_redis_queue():
    # screenshots 폴더가 이미 존재하면 아카이빙
    output_dir = 'screenshots'
    if os.path.exists(output_dir):
        archive_screenshots(output_dir)
        # 기존 폴더 삭제
        shutil.rmtree(output_dir)

    # Redis 서버에 연결
    r = redis.Redis()
    # carrot_tasks 큐를 비우기
    r.delete('carrot_tasks')
    print("Redis queue 'carrot_tasks' has been cleared")


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

            # 종료된 프로세스 청소
            processes = [p for p in processes if p.is_alive()]

            # 모든 프로세스가 종료되었고, 더 이상 처리할 작업이 없을 때 종료
            if len(processes) == 0 and current_length == 0:
                break

            print(f'Current Queue length: {current_length}')
            print(f'Current processes: {len(processes)}')

            for p in processes:
                print(f'Process {p.pid} is alive: {p.is_alive()}')

            # 새로운 프로세스 시작 조건
            while len(processes) < max_processes and current_length > 0:
                p = Process(target=consumer_task)
                p.start()
                processes.append(p)
                print(f'Started process {p.pid}')

            time.sleep(1)  # CPU 사용률을 관리하기 위한 간단한 딜레이
        # for p in processes:
        #     p.terminate()
    except KeyboardInterrupt:
        # Ctrl+C를 눌렀을 때 모든 프로세스 정리
        for p in processes:
            if p.is_alive():
                p.terminate()
            p.join()
        processes = []


if __name__ == '__main__':
    # argparse 라이브러리를 사용하여 명령줄 인터페이스 구성
    parser = argparse.ArgumentParser(description='Carrot Market Scraping')

    # 최대 소비자 프로세스 수를 명령줄에서 입력받음. 기본값은 3.
    parser.add_argument('--max_processes', type=int, default=3,
                        help='Maximum number of consumer processes to run. Default is 3.')

    # 스크래핑을 시작할 게시글의 시작 인덱스 번호를 명령줄에서 입력받음. 기본값은 783227594.
    parser.add_argument('--index', type=int, default=783227594,
                        help='Starting index number for the articles. Default is 783227594.')

    # 스크래핑할 게시글의 수를 명령줄에서 입력받음. 기본값은 100.
    parser.add_argument('--count', type=int, default=100,
                        help='Number of articles to scrape. Default is 100.')

    # 입력된 인자들을 파싱하여 args 객체로 만듦
    args = parser.parse_args()

    # 파싱된 인자들을 개별 변수에 저장
    max_processes = args.max_processes  # 사용할 최대 프로세스 수
    start_index = args.index            # 스크래핑 시작 게시글 인덱스
    count = args.count                  # 스크래핑할 게시글 수

    # 당근 마켓 게시글 URL
    url = 'https://www.daangn.com/articles/'

    # 크롤링할 URL 리스트 초기화
    urls_to_scrape = []

    # 지정된 개수만큼 게시글 URL을 크롤링할 URL 리스트에 추가
    for i in range(count):
        tmp_index = start_index - i
        article_url = f'{url}{tmp_index}'
        urls_to_scrape.append(article_url)

    # Redis 큐 초기화
    initialize_redis_queue()

    # 프로듀서 작업 수행
    producer_task(urls_to_scrape)

    # 소비자 프로세스 관리 시작
    manage_consumers(max_processes)

    # 모든 작업이 Redis 큐에 추가되고 소비자 프로세스 관리가 완료된 후 메시지 출력
    time.sleep(1.5)
    print("All tasks have been added to the queue and consumer management has completed. Shutting down producer process.")

    # 프로듀서 프로세스 종료
    sys.exit(0)
