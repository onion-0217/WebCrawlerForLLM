import pandas as pd
from konlpy.tag import Okt
import re
import os
import glob

# ==========================================
# 1. 설정 및 파일 목록 불러오기
# ==========================================
DATA_DIR = "naver_news_data"
FILE_PATTERN = os.path.join(DATA_DIR, "naver_news_*.csv")
OUTPUT_FILE = "train_style_data.txt"

all_files = sorted(glob.glob(FILE_PATTERN))

if not all_files:
    print(f"❌ 오류: '{DATA_DIR}' 폴더에 파일이 없습니다.")
    exit()

print(f"📂 총 {len(all_files)}개의 파일을 발견했습니다.")

# 형태소 분석기 초기화
okt = Okt()
training_data = []

# ==========================================
# 🔥 [핵심] 블랙리스트(불용어) 정의
# 뉴스 제목에 자주 나오지만, 키워드로는 쓸모없는 단어들입니다.
# ==========================================
STOP_WORDS = {
    '이번', '지난', '오늘', '내일', '모레', '관련', '대해', '가장',
    '통해', '위해', '경우', '때문', '정도', '부분', '사실', '이제',
    '다시', '계속', '지금', '바로', '역시', '그냥', '자신', '진짜',
    '이형', '그것', '누구', '무엇', '어디', '언제', '우리', '당신',
    '최근', '단독', '속보', '종합', '오전', '오후', '하루', '이형',
    '모두', '내년', '어제', '하나', '다섯', '여섯', '일곱', '여덟',
    '아홉', '주간', '매일', '올해', '미만', '내년', '이상', '작년',
    '이하', '초과', '개월', '앞서', '개월', '이틀', '사흘', '나흘',
    '글피'
}

print("\n🚀 데이터 전처리를 시작합니다 (불용어 제거 포함)...")

total_articles = 0

for i, file_path in enumerate(all_files):
    filename = os.path.basename(file_path)
    print(f"[{i + 1}/{len(all_files)}] '{filename}' 처리 중...", end=" ")

    try:
        df = pd.read_csv(file_path)
        current_file_count = 0

        for index, row in df.iterrows():
            try:
                raw_title = str(row['title'])
                press = str(row['press'])

                # 특수문자 청소
                clean_title = re.sub(r'\[.*?\]|\(.*?\)|\<.*?\>', '', raw_title)
                clean_title = clean_title.strip()

                # 명사 추출
                nouns = okt.nouns(clean_title)

                # 1. 두 글자 이상이어야 함 (len > 1)
                # 2. 블랙리스트에 없어야 함 (not in STOP_WORDS)
                filtered_nouns = [
                    n for n in nouns
                    if len(n) > 1 and n not in STOP_WORDS
                ]

                # 필터링 후 남은 게 없으면 패스
                if not filtered_nouns:
                    continue

                # 키워드 조합 (최대 3개)
                keywords = ", ".join(filtered_nouns[:3])

                formatted_text = f"[{press}] {keywords}: {clean_title} </s>"
                training_data.append(formatted_text)
                current_file_count += 1

            except Exception:
                continue

        total_articles += current_file_count
        print(f"✅ 완료 ({current_file_count}개)")

    except Exception as e:
        print(f"❌ 실패: {e}")

# 저장
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for line in training_data:
        f.write(line + "\n")

print("\n" + "=" * 50)
print(f"🎉 작업 완료! 총 {total_articles}개 문장 생성")
print(f"💾 저장 위치: {OUTPUT_FILE}")
print("=" * 50)