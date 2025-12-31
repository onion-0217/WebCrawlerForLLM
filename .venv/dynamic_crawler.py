from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

print("🚀 브라우저를 실행합니다...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 데이터 저장소
data = []
gallery_id = 'programming'

#글 번호(존재해야 에러가 나지 않음)
start_no = 2526000
end_no = 2526005

try:
    for no in range(start_no, end_no + 1):
        url = f"https://gall.dcinside.com/board/view/?id={gallery_id}&no={no}"

        try:
            print(f"\n▶ {no}번 글 이동 중...")
            driver.get(url)

            time.sleep(random.uniform(2, 3))

            # [삭제된 글 감지] 제목 요소가 없으면 삭제된 글일 확률이 높음
            try:
                # 제목 찾기
                title_element = driver.find_element(By.CSS_SELECTOR, '.title_subject')
                # 본문 찾기
                content_element = driver.find_element(By.CSS_SELECTOR, '.write_div')
            except:
                print("   ❌ 삭제되었거나 존재하지 않는 글입니다.")
                continue

            # 데이터 추출 (.text 필수)
            post = {
                'no': no,
                'title': title_element.text,
                'content': content_element.text,
                'url': url
            }

            data.append(post)
            print(f"   ✅ 수집 성공: {post['title'][:10]}...")  # 제목 앞부분만 출력

        except Exception as e:
            print(f"   ⚠️ 개별 글 수집 중 에러: {e}")
            continue

except KeyboardInterrupt:
    print("\n강제 종료됨!")

finally:
    # 결과 확인
    print("\n" + "=" * 30)
    print(f"총 {len(data)}개의 글을 수집했습니다.")
    print(data)  # 리스트[딕셔너리] 형태 출력

    driver.quit()