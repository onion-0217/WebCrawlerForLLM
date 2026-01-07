import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import os

# ==============================================================================
# [1] 설정 영역
# ==============================================================================
START_DATE = "20220101"  # 수집 시작 날짜
END_DATE = "20251231"  # 수집 종료 날짜
OUTPUT_DIR = "naver_news_data"  # 저장할 폴더명

# ==============================================================================
# [2] 초기 설정 및 헤더 준비
# ==============================================================================
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 사람인 척 위장하는 기본 헤더
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}


# 날짜 리스트 생성 함수
def get_date_range(start, end):
    start_dt = datetime.strptime(start, "%Y%m%d")
    end_dt = datetime.strptime(end, "%Y%m%d")
    delta = end_dt - start_dt
    return [(start_dt + timedelta(days=i)).strftime("%Y%m%d") for i in range(delta.days + 1)]


date_list = get_date_range(START_DATE, END_DATE)

# 변수 초기화
total_collected = 0
current_month_data = []
last_saved_month = ""
previous_url = "https://news.naver.com/"

print(f"🚀 [최종본] 크롤러 시작! ({START_DATE} ~ {END_DATE})")
print(f"📂 데이터는 '{OUTPUT_DIR}' 폴더에 월별로 저장됩니다.\n")

# ==============================================================================
# [3] 메인 수집 루프
# ==============================================================================
for idx, target_date in enumerate(date_list):
    # 정확한 랭킹 뉴스 URL
    url = f"https://news.naver.com/main/ranking/popularDay.naver?date={target_date}"

    # [핵심] Referer를 계속 바꿔서 '링크를 타고 들어온 척' 위장
    headers['Referer'] = previous_url

    try:
        response = requests.get(url, headers=headers, timeout=10)

        # 접속 실패 시 건너뜀
        if response.status_code != 200:
            print(f"❌ {target_date} 접속 실패 (Status: {response.status_code})")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # ----------------------------------------------------------------------
        # [4] 데이터 파싱
        # ----------------------------------------------------------------------
        press_boxes = soup.select('.rankingnews_box')
        daily_count = 0

        for box in press_boxes:
            try:
                # 언론사 이름
                press_name = box.select_one('.rankingnews_name').text.strip()

                # 기사 리스트
                ranks = box.select('.rankingnews_list > li')

                for rank_idx, li in enumerate(ranks):
                    # 제목 태그 찾기
                    title_tag = li.select_one('.list_title')
                    if not title_tag:
                        title_tag = li.select_one('a')

                    if title_tag:
                        title = title_tag.text.strip()
                        link = title_tag.get('href')

                        current_month_data.append({
                            'date': target_date,
                            'rank': rank_idx + 1,
                            'press': press_name,
                            'title': title,
                            'link': link
                        })
                        daily_count += 1
            except Exception as e:
                continue  # 특정 기사 파싱 에러는 무시하고 계속 진행

        total_collected += daily_count

        # 진행 상황 출력 (Referer 뒷부분만 보여줌)
        print(f"   ✅ {target_date} (Ref: ...{previous_url[-15:]}): {daily_count}개 수집")

        # ----------------------------------------------------------------------
        # [5] 안전 장치 및 저장 로직
        # ----------------------------------------------------------------------

        # 다음 턴을 위해 현재 URL을 '이전 URL'로 저장
        previous_url = url

        # 랜덤 대기 (0.5 ~ 1.5초)
        time.sleep(random.uniform(0.5, 1.5))

        # 30일마다 브라우저 패턴 리셋 (메인으로 돌아가는 척) + 5초 휴식
        if idx > 0 and idx % 30 == 0:
            print("   ☕ 패턴 리셋 및 휴식 중...")
            time.sleep(5)
            previous_url = "https://news.naver.com/"

        # 월이 바뀌면 파일 저장 (메모리 관리)
        current_month = target_date[:6]
        if last_saved_month != "" and current_month != last_saved_month:
            if current_month_data:
                save_path = f"{OUTPUT_DIR}/naver_news_{last_saved_month}.csv"
                df = pd.DataFrame(current_month_data)
                df.to_csv(save_path, index=False, encoding='utf-8-sig')
                print(f"   💾 [저장] {last_saved_month} 데이터 저장 완료 ({len(df)}건)")
                current_month_data = []  # 리스트 초기화

        last_saved_month = current_month

    except Exception as e:
        print(f"   ⚠️ 에러 발생 ({target_date}): {e}")
        time.sleep(10)  # 에러나면 10초 대기

# ==============================================================================
# [6] 남은 데이터 최종 저장
# ==============================================================================
if current_month_data:
    save_path = f"{OUTPUT_DIR}/naver_news_{last_saved_month}.csv"
    df = pd.DataFrame(current_month_data)
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"   💾 [최종 저장] {last_saved_month} 데이터 저장 완료")

print("\n" + "=" * 50)
print(f"🎉 모든 수집이 완료되었습니다!")
print(f"총 수집된 데이터: {total_collected}건")
print("=" * 50)