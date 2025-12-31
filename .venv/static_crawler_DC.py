import requests
from bs4 import BeautifulSoup
import time
import random

# 설정
base_url = "https://gall.dcinside.com/board/lists/"
gallery_id = 'blackwhites2'  # 갤러리 ID

# 기본 헤더 (User-Agent는 고정)
default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# 수집하고 싶은 페이지 범위 설정 (예: 1페이지부터 5페이지까지)
start_page = 1
end_page = 5

print(f"🚀 [{gallery_id}] 갤러리 {start_page}~{end_page}페이지 크롤링 시작...\n")

for page in range(start_page, end_page + 1):
    # ---------------------------------------------------------
    # 1. [핵심] 페이지 번호와 Referer를 동적으로 변경하는 부분
    # ---------------------------------------------------------

    # 파라미터 업데이트 (page=1, page=2, ...)
    params = {'id': gallery_id, 'page': str(page)}

    # Referer 업데이트
    # (사람이 1페이지를 보고 2페이지를 누르는 것처럼 보이게, 이전 페이지 주소나 현재 리스트 주소를 넣어줍니다)
    # 여기서는 요청하신 대로 해당 페이지 정보를 담은 Referer를 생성합니다.
    current_referer = f"https://gall.dcinside.com/board/lists/?id={gallery_id}&page={page}"

    # 헤더 복사 후 Referer 추가
    headers = default_headers.copy()
    headers['Referer'] = current_referer

    print(f"▶ {page} 페이지 수집 중... (Referer: ...&page={page})")

    try:
        # 요청 보내기
        response = requests.get(base_url, params=params, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select('.ub-content.us-post')

            if not rows:
                print("글이 없거나 차단되었을 수 있습니다.")
                continue

            # 글 목록 추출
            for row in rows:
                title_tag = row.select_one('.gall_tit > a')
                num_tag = row.select_one('.gall_num')

                if title_tag and num_tag:
                    title = title_tag.get_text(strip=True)
                    num = num_tag.get_text(strip=True)

                    # 공지사항 제외하고 숫자만 출력하고 싶다면 아래 주석 해제
                    # if not num.isdigit(): continue

                    print(f"[{num}] {title}")
        else:
            print(f"접속 실패! 상태 코드: {response.status_code}")

    except Exception as e:
        print(f"   에러 발생: {e}")

    # ---------------------------------------------------------
    # 2. [필수] 다음 페이지로 넘어가기 전 랜덤하게 쉬기
    # ---------------------------------------------------------
    if page < end_page:  # 마지막 페이지가 아닐 때만 대기
        wait_time = random.uniform(2, 5)  # 2초에서 5초 사이 랜덤
        print(f"\n⏳ {wait_time:.1f}초 대기 후 다음 페이지로 이동합니다...")
        time.sleep(wait_time)

print("\n✅ 모든 수집이 완료되었습니다!")