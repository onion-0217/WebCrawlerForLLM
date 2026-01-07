import requests
from bs4 import BeautifulSoup
import time
#requests - 웹 서버에 페이지 내용을 요청하고 받아오는 역할
#BeautifulSoup - 받아온 HTML 코드를 분석해서 데이터를 정제하는 역할

#1. 네이버 뉴스(IT/과학 테마)
##########
#단 robot.txt에 의거 이 행동은 불법이다. 연습을 위한 전용 사이트 Books to Scrape를 이용하자.
##########
url = 'https://news.naver.com/section/105'


#2. 헤더 설정 (중요: 봇이 아닌 일반 브라우저처럼 보이기 위함)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

#3. 서버에 요청 보내기
response = requests.get(url, headers=headers)

#4. 응답 확인 (200이면 성공)
if response.status_code == 200:
    #5. HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    #6. 원하는 요소 찾기
    #ex) 기사 제목이 <strong class="sa_text_strong"> ~ </strong>인 경우 아래
    titles = soup.select('.sa_text_strong')

    #7. 데이터 출력
    #
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title.get_text().strip()}")
else:
    print(f"Error: {response.status_code}")
