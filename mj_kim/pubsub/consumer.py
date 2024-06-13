import redis
import json
import subprocess
import os
import time
from multiprocessing import Process

# 프로세스 수
MAX_PROCESSES = 3

def capture_webpage(url, output_dir):
    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # URL에서 파일 이름을 추출
    file_name = url.split('/')[-1]
    print(f'Capturing {url} to {file_name}.pdf')

    # wkhtmltopdf 명령을 이용해 URL을 PDF로 변환
    output_file = os.path.join(output_dir, f"{file_name}.pdf")
    command = f"wkhtmltopdf {url} {output_file} > /dev/null 2>&1"

    # 명령 실행
    subprocess.run(command, shell=True)
    print(f'Saved {url} to {output_file}')


def consumer_task():
    # Redis 서버에 연결
    r = redis.Redis()
    start_time = time.time()
    while True:

        # 블로킹 방식으로 메시지를 가져옴
        task = r.brpop('carrot_tasks')
        if task:
            # 메시지를 JSON 형식으로 변환한 후 URL을 추출
            task_data = json.loads(task[1])
            url = task_data['url']

            # URL을 이용한 크롤링 작업
            # argument로 URL을 전달하고, 출력 파일을 저장할 디렉토리를 지정
            capture_webpage(url, 'screenshots')


def manage_consumers():
    # 프로세스 관리 리스트
    processes = []
    start_time = time.time()

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
        time.sleep(1)

    # 모든 프로세스가 종료될 때까지 대기
    for p in processes:
        p.join()
        print(f'Joined process {p.pid}')


if __name__ == '__main__':
    # 소비자 프로세스를 시작
    manage_consumers()
