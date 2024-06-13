import requests
from bs4 import BeautifulSoup
import time
import os

start_time = time.time()

url = 'https://www.daangn.com/articles/'
index = 783227594

for i in range(0, 100):
    file_name = f'dg_{index - i}'

    print(f'Processing {index - i}...')

    tmp_index = index - i
    article_url = f'{url}{tmp_index}'
    response = requests.get(article_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            title = soup.find('h1', id='article-title')
            title_text = title.get_text(strip=True)
        except:
            title_text = 'Title not found'

        img_url = 'Image not found'

        try:
            images_section = soup.find('section', id='article-images')
            if images_section:
                img_tags = images_section.find_all('img')
                for img in img_tags:
                    img_url = img.get('data-lazy').split('?')[0]
                    img_response = requests.get(img_url, stream=True)
                    if img_response.status_code == 200:
                        img_response.raw.decode_content = True
                        with open(f'{file_name}.jpg', 'wb') as img_file:
                            img_file.write(img_response.content)
                    break  # 첫 번째 이미지만 저장하고 반복문 종료

        except:
            img_url = 'Image not found'

        with open(file_name, 'w') as file:
            file.write(f'URL: {article_url}\n')
            file.write(f'Title: {title_text}\n')

    else:
        print(f'Status code: {response.status_code}')

print(f'Total time: {time.time() - start_time} seconds')
