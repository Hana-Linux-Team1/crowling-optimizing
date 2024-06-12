import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor

def process_article(index):
    url = 'https://www.daangn.com/articles/'
    file_name = f'dg_{index}'
    article_url = f'{url}{index}'

    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            title = soup.find('h1', id='article-title')
            title_text = title.get_text(strip=True) if title else 'Title not found'
        except Exception as e:
            title_text = 'Title not found'
            print(f'Error extracting title: {e}')

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
        except Exception as e:
            img_url = 'Image not found'
            print(f'Error extracting image: {e}')

        try:
            with open(file_name + '.txt', 'w') as file:
                file.write(f'URL: {article_url}\n')
                file.write(f'Title: {title_text}\n')
            #print(f'Successfully created {file_name}.txt')
        except Exception as e:
            print(f'Error writing file {file_name}.txt: {e}')
    else:
        #print(f'Status code: {response.status_code}')
        with open(file_name+'.txt', 'w') as file:
            file.write(f'URL: {article_url}\n')
            file.write(f'Status code: {response.status_code}\n')
    #print(f'Finished processing {index}.')

def main():
    start_time = time.time()
    index = 783227594
    num_threads = 15  # 사용할 스레드 수
    indices = [index - i for i in range(100)]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(process_article, indices)

    print(f'Total time: {time.time() - start_time} seconds')

if __name__ == '__main__':
    main()
