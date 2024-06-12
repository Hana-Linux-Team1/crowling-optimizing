import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time

async def fetch(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            return None, None, url
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
        try:
            title = soup.find('h1', id='article-title')
            title_text = title.get_text(strip=True) if title else 'Title not found'
        except:
            title_text = 'Title not found'

        img_url = 'Image not found'
        try:
            images_section = soup.find('section', id='article-images')
            if images_section:
                img_tags = images_section.find_all('img')
                for img in img_tags:
                    img_url = img.get('data-lazy').split('?')[0]
                    break  # 첫 번째 이미지 URL만 가져오기
        except:
            pass

        return title_text, img_url, url

async def fetch_image(session, img_url, file_name):
    if not isinstance(img_url, str) or img_url == 'Image not found':
        return
    async with session.get(img_url) as img_response:
        if img_response.status == 200:
            with open(f'{file_name}.jpg', 'wb') as img_file:
                img_file.write(await img_response.read())

async def main():
    url = 'https://www.daangn.com/articles/'
    index = 783227594

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(0, 100):
            file_name = f'dg_{index - i}'
            tmp_index = index - i
            article_url = f'{url}{tmp_index}'
            tasks.append(fetch(session, article_url))

        results = await asyncio.gather(*tasks)

        for title_text, img_url, article_url in results:
            file_name = f'dg_{index - (int(article_url.split("/")[-1]) - index)}'
            with open(file_name+'.txt', 'w') as file:
                file.write(f'URL: {article_url}\n')
                file.write(f'Title: {title_text}\n')

            await fetch_image(session, img_url, file_name)

start_time = time.time()
asyncio.run(main())
print(f'Total time: {time.time() - start_time} seconds')
