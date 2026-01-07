import pandas as pd
from konlpy.tag import Okt
import re
import os
import glob

# ==========================================
# 1. 설정 및 파일 목록 불러오기
# ==========================================
# 데이터가 들어있는 폴더 경로와 파일 패턴
DATA_DIR = "naver_news_data"
FILE_PATTERN = os.path.join(DATA_DIR, "naver_news_*.csv")
OUTPUT_FILE = "train_style_data.txt"

# 패턴에 맞는 파일들을 모두 찾아서 정렬 (202201 -> 202512 순서대로)
all_files = sorted(glob.glob(FILE_PATTERN))

if not all_files:
    print(f"❌ 오류: '{DATA_DIR}' 폴더 안에 'naver_news_'로 시작하는 파일이 하나도 없습니다.")
    exit()

print(f"📂 총 {len(all_files)}개의 파일을 발견했습니다.")
print(f"   - 첫 번째 파일: {os.path.basename(all_files[0])}")
print(f"   - 마지막 파일: {os.path.basename(all_files[-1])}")

# 형태소 분석기 초기화
okt = Okt()
training_data = []

print("\n🚀 대규모 데이터 전처리를 시작합니다...")

# ==========================================
# 2. 모든 파일을 순회하며 데이터 정제
# ==========================================
total_articles = 0  # 총 기사 개수 카운트용

for i, file_path in enumerate(all_files):
    filename = os.path.basename(file_path)
    print(f"[{i + 1}/{len(all_files)}] '{filename}' 처리 중...", end=" ")

    try:
        # csv 파일 읽기
        df = pd.read_csv(file_path)

        # 각 기사별 처리
        current_file_count = 0
        for index, row in df.iterrows():
            try:
                raw_title = str(row['title'])
                press = str(row['press'])

                # [Re 모듈] 특수문자 및 말머리 청소
                clean_title = re.sub(r'\[.*?\]|\(.*?\)|\<.*?\>', '', raw_title)
                clean_title = clean_title.strip()

                # 1. 명사 추출
                nouns = okt.nouns(clean_title)

                # 2. 한 글자 제거 (필터링)
                filtered_nouns = [n for n in nouns if len(n) > 1]

                # 3. 필터링된 결과가 비어있으면 건너뛰기
                if not filtered_nouns:
                    continue

                # 4. 키워드 조합 (필터링된 명사 사용)
                keywords = ", ".join(filtered_nouns[:3])

                # [학습 데이터 포맷]
                formatted_text = f"[{press}] {keywords}: {clean_title} </s>"

                training_data.append(formatted_text)
                current_file_count += 1

            except Exception:
                continue

        total_articles += current_file_count
        print(f"✅ 완료 ({current_file_count}개 추출)")

    except Exception as e:
        print(f"❌ 파일 읽기 실패: {e}")

# ==========================================
# 3. 결과 저장하기
# ==========================================
print("\n" + "="*50)
print("💾 결과 파일 저장 중...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for line in training_data:
        f.write(line + "\n")

print(f"🎉 모든 작업 완료!")
print(f"📊 총 처리된 파일: {len(all_files)}개")
print(f"📝 생성된 학습 문장: {total_articles}개")
print(f"파일 위치: {os.path.abspath(OUTPUT_FILE)}")
print("="*50)