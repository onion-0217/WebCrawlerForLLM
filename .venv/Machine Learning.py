import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline

# 1. 데이터 로드 및 전처리 (자동 인코딩 감지)
try:
    df = pd.read_csv('titiles_and_views.csv', encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv('titiles_and_views.csv', encoding='cp949')

# 데이터 정제 (중복/결측치 제거)
df = df.drop_duplicates().dropna()

# 조회수(views) 숫자 변환 (쉼표 제거)
if df['views'].dtype == 'object':
    df['views'] = df['views'].astype(str).str.replace(',', '').astype(int)

# 2. 머신러닝 학습 (텍스트 -> 조회수 예측)
# Tfidf: 단어의 중요도 분석 (1~2단어 조합)
vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=10)
model = Ridge(alpha=1.0) # 회귀 모델

# 파이프라인으로 학습
pipeline = make_pipeline(vectorizer, model)
pipeline.fit(df['title'], df['views'])

# 3. 결과 추출: 조회수에 긍정적인 영향을 주는 단어 Top 20
feature_names = vectorizer.get_feature_names_out()
coefficients = model.coef_

# 중요도 순으로 정렬
top_features = pd.DataFrame({'word': feature_names, 'score': coefficients})
top_features = top_features.sort_values(by='score', ascending=False).head(20)

print("=== 조회수 떡상 키워드 Top 20 ===")
print(top_features)