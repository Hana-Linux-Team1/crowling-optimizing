import redis
import json
import subprocess
import os
import requests


def capture_webpage(url, output_dir):
    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # URL에서 파일 이름을 추출
    file_name = url.split('/')[-1]
    print(f'Capturing {url} to {file_name}.png')

    # wkhtmltoimage 명령을 이용해 URL을 PNG로 변환
    output_file = os.path.join(output_dir, f"{file_name}.png")
    command = f"wkhtmltoimage {url} {output_file} > /dev/null 2>&1"

    # 명령 실행
    subprocess.run(command, shell=True)
    print(f'Saved {url} to {output_file}')


def consumer_task():
    # Redis 서버에 연결
    r = redis.Redis()
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


if __name__ == '__main__':
    consumer_task()
