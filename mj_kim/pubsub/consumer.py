import redis
import json
import subprocess
import os
import time
from multiprocessing import Process

MAX_PROCESSES = 3


def capture_webpage(url, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = url.split('/')[-1]
    print(f'Capturing {url} to {file_name}.pdf')

    output_file = os.path.join(output_dir, f"{file_name}.pdf")
    command = f"wkhtmltopdf {url} {output_file} > /dev/null 2>&1"
    subprocess.run(command, shell=True)
    print(f'Saved {url} to {output_file}')


def consumer_task():
    r = redis.Redis()
    while True:
        task = r.brpop('carrot_tasks')
        if task:
            task_data = json.loads(task[1])
            url = task_data['url']
            capture_webpage(url, 'screenshots')


def manage_consumers():
    processes = []
    while True:
        if len(processes) < MAX_PROCESSES:
            p = Process(target=consumer_task)
            p.start()
            processes.append(p)
            print(f'Started process {p.pid}')
        else:
            for p in processes:
                if not p.is_alive():
                    processes.remove(p)
                    print(f'Terminated process {p.pid}')
        time.sleep(1)


if __name__ == '__main__':
    manage_consumers()
