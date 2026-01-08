import torch
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel

# ==========================================
# 1. 저장된 모델 불러오기
# ==========================================
MODEL_PATH = "news_title_model"


device = torch.device("cpu")

print("📂 학습된 모델을 로딩 중입니다...")
try:
    tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_PATH)
    model = GPT2LMHeadModel.from_pretrained(MODEL_PATH)
    model.to(device)
    print("✅ 모델 로딩 완료!")
except Exception as e:
    print(f"❌ 오류: {e}")
    exit()


# ==========================================
# 2. 제목 생성 함수
# ==========================================
def generate_title(press, keywords):
    # 입력 형식: [언론사] 키워드:
    prompt = f"[{press}] {keywords}:"

    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    # AI에게 뒷내용(제목) 쓰라고 시키기
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length=64,
            num_beams=5,  # 5개 후보 중 베스트 선택
            temperature=1.0, #1위의 점수를 균등 분배
            top_k=50, #상위 50등 중에서
            top_p=0.95, #확률 95% 이상만
            no_repeat_ngram_size=2,  # 같은 단어 반복 금지
            repetition_penalty=1.5, #반복시 패널티점수
            early_stopping=True,
            eos_token_id=tokenizer.eos_token_id,
            do_sample=True
        )

    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text


# ==========================================
# 3. 실전 테스트
# ==========================================
print("\n" + "=" * 50)
print("🤖 강민이의 AI 뉴스 편집기 (종료: q)")
print("=" * 50)

while True:
    print("\n------------------------------------------------")
    press = input("📰 언론사 (예: 조선일보): ").strip()
    if press == 'q': break

    keywords = input("🔑 키워드 (예: 이재명, 검찰): ").strip()
    if keywords == 'q': break

    print("⏳ 제목 뽑는 중...", end="")
    try:
        result = generate_title(press, keywords)
        # 결과에서 입력한 프롬프트 부분은 빼고 제목만 보여주기
        clean_result = result.replace(f"[{press}] {keywords}:", "").strip()
        print(f"\r👉 결과: {clean_result}")
    except Exception as e:
        print(f"\n❌ 생성 실패: {e}")