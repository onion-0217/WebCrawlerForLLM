from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import requests
import pandas as pd

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
start_page = 1
end_page = 10

try:
    for page in range(start_page, end_page + 1):
        url = f"https://gall.dcinside.com/board/lists/?id={gallery_id}&page={page}"

        try:
            print(f"\n▶ {page} 쪽 이동 중...")
            driver.get(url)

            time.sleep(random.uniform(2, 3))

            rows = driver.find_elements(By.CSS_SELECTOR, '.ub-content.us-post')

            if not rows:
                print("   ⚠️ 글을 찾을 수 없습니다. (차단되었거나 없는 페이지)")
                continue

            for row in rows:
                try:
                    title_element = row.find_element(By.CSS_SELECTOR, '.gall_tit > a')
                    view_element = row.find_element(By.CSS_SELECTOR, '.gall_count')

                    post = {
                        'title': title_element.text.strip(),
                        'views': view_element.text.strip()
                    }
                    data.append(post)

                except Exception:
                    continue  # 광고나 공지사항 등 구조가 다르면 패스

            print(f"   ✅ {page}페이지 수집 완료 (현재 누적 {len(data)}개)")

        except Exception as e:
            print(f"   ⚠️ 페이지 접속 에러: {e}")
        continue

except KeyboardInterrupt:
    print("\n강제 종료됨!")

finally:
    # 결과 확인
    print("\n" + "=" * 30)
    print(f"총 {len(data)}개의 글을 수집했습니다.")
    print(data)  # 리스트[딕셔너리] 형태 출력

    driver.quit()

df = pd.DataFrame(data)

#조회수를 숫자로 변경, '-'따위의 문자는 0으로 처리
df['views'] = pd.to_numeric(df['views'].str.replace(',',''), errors='coerce').fillna(0).astype(int)

df.to_csv('titiles_and_views.csv', index=False, encoding='utf-8')

print(df.head())