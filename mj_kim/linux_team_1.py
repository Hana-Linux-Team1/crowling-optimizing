import requests
from bs4 import BeautifulSoup
import time

start_time = time.time()

file_name = 'result.txt'

url = 'https://www.daangn.com/articles/'

index = 783227594

for i in range(0, 10):
  print(f'Processing {index - i}...')
  tmp_index = index - i
  url = 'https://www.daangn.com/articles/' + str(tmp_index)
  response = requests.get(url)
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
    except:
      img_url = 'Image not found'
    
    with open(file_name, 'a') as file:
        file.write(f'URL: {url}\n')
        file.write(f'Title: {title_text}\n')
        file.write(f'Image URL: {img_url}\n')
        file.write(f'==================================\n')
    
  else:
    print(f'Status code: {response.status_code}')
    
    with open(file_name, 'a') as file:
        file.write(f'URL: {url}\n')
        file.write(f'Status code: {response.status_code}\n')
        file.write(f'==================================\n')
    
end_time = time.time()
elapsed_time = end_time - start_time
with open(file_name, 'a') as file:
    file.write(f'걸린 시간: {elapsed_time} seconds\n')
