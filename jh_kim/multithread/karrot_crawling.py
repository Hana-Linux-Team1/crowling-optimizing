import requests
from bs4 import BeautifulSoup
import time
import os
from threading import Thread
from multiprocessing import Process, Queue, Pool


def karrot_crawling(p_num):
    url = 'https://www.daangn.com/articles/'+str(p_num)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # file = open('./crawling.txt','w')
    # 페이지 요청
    response = requests.get(url, headers=headers)

    # 요청이 성공적인지 확인
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 제목 추출
        title_tag = soup.find('h1', class_='hide')
        title = title_tag.get_text(strip=True) if title_tag else '제목 없음'

        # 가격 추출
        price_tag = soup.find('p', id='article-price')
        price = price_tag.get_text(strip=True) if price_tag else '가격 없음'

        # 설명 추출
        description_tag = soup.find('div', id='article-detail')
        description = ''
        if description_tag:
            for br in description_tag.find_all('br'):
                br.replace_with('\n')
            description = description_tag.get_text(strip=True)
        else:
            description ='설명 없음'
        
        # 이미지 url 추출
        try:
            img_url = soup.find('div', class_='image-wrap').find('img')['data-lazy']
        except:
            img_url = '이미지 없음'
        # img_url = img_url_tag.get_text(strip=True) if img_url_tag else 'url 없음'
        
        # 위치 추출
        location_tag = soup.find('div', id='region-name')
        location = location_tag.get_text(strip=True) if location_tag else '위치 없음'

        # 추출된 데이터 출력
        print('제목:', title)
        print('가격:', price)
        print('설명:', description)
        print('위치:', location)
        print('이미지 url', img_url)
        print('============================================================\n')
        
        # file.write('제목:'+ title+'\n')
        # file.write('가격:'+ price+'\n')
        # file.write('설명:'+ description+'\n')
        # file.write('위치:'+ location+'\n')
        # file.write('이미지 url'+img_url+'\n')
        # file.write('============================================================\n')

    else:
        print('페이지 요청에 실패했습니다. 상태 코드:', response.status_code)
    # file.close()
    
if __name__ == '__main__':
    p_num = 780003799
    start_time = time.time()

    # 크롤링할 페이지 번호 리스트 생성
    page_numbers = [p_num + i for i in range(100)]

    # 멀티프로세싱 풀 생성
    with Pool(processes=4) as pool:  # 프로세스 수 조절 가능
        pool.map(karrot_crawling, page_numbers)

    end_time = time.time()
    print("총 소요 시간: ", round(end_time - start_time, 4), " 초")
