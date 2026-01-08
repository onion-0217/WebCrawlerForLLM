import torch
from torch.utils.data import Dataset, DataLoader
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
from torch.optim import AdamW
import os
from tqdm import tqdm  # 진행률 표시바

# ==========================================
# 1. 설정
# ==========================================
EPOCHS = 3  # 학습 횟수 (횟수가 늘어나면 과적합 문제 발생)
BATCH_SIZE = 8  # 한 번에 공부할 문제 수
LEARNING_RATE = 3e-5  # 학습 속도
MAX_LEN = 64  # 문장의 최대 길이 (제목이니까 짧게 64로 설정)

DATA_PATH = "train_style_data.txt"
MODEL_NAME = "skt/kogpt2-base-v2"
OUTPUT_DIR = "news_title_model"  # 학습된 모델이 저장될 폴더

# GPU가 있으면 쓰고, 없으면 CPU를 씁니다
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 학습 장치: {device}")


# ==========================================
# 2. 데이터셋 클래스 (데이터를 AI에게 떠먹여주는 숟가락)
# ==========================================
class NewsTitleDataset(Dataset):
    def __init__(self, file_path, tokenizer, max_len):
        self.data = []
        self.tokenizer = tokenizer
        self.max_len = max_len

        print("📂 데이터를 로딩 중입니다...")
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in tqdm(lines):
            line = line.strip()
            if not line: continue

            # 토크나이징 (글자를 숫자로 변환)
            tokenized = tokenizer(
                line,
                padding="max_length",
                truncation=True,
                max_length=max_len,
                return_tensors="pt"
            )

            self.data.append({
                "input_ids": tokenized["input_ids"][0],
                "attention_mask": tokenized["attention_mask"][0]
            })

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


# ==========================================
# 3. 학습 실행 (메인 로직)
# ==========================================
def main():
    # 토크나이저 & 모델 불러오기 (SKT KoGPT2)
    tokenizer = PreTrainedTokenizerFast.from_pretrained(
        MODEL_NAME,
        bos_token='</s>',
        eos_token='</s>',
        unk_token='<unk>',
        pad_token='<pad>',
        mask_token='<mask>'
    )

    model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)
    model.to(device)
    model.train()  # 학습 모드로 전환

    # 데이터 로더 준비
    dataset = NewsTitleDataset(DATA_PATH, tokenizer, MAX_LEN)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # 최적화 도구 (Optimizer) 설정
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

    print(f"\n🚀 학습을 시작합니다! (총 {len(dataset)}개 문장, {EPOCHS} 에폭)")

    for epoch in range(EPOCHS):
        total_loss = 0
        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch + 1}/{EPOCHS}")

        for batch in progress_bar:
            optimizer.zero_grad()  # 이전 기울기 초기화

            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            # 모델에게 정답지(labels)를 주면 알아서 loss를 계산함
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=input_ids
            )

            loss = outputs.loss
            loss.backward()  # 역전파 (오답노트 작성)
            optimizer.step()  # 가중치 업데이트 (공부 내용 반영)

            total_loss += loss.item()
            progress_bar.set_postfix({'loss': f"{loss.item():.4f}"})

        avg_loss = total_loss / len(dataloader)
        print(f"📊 Epoch {epoch + 1} 종료 - 평균 Loss: {avg_loss:.4f}")

        # 에폭마다 모델 저장
        model.save_pretrained(f"{OUTPUT_DIR}/checkpoint-{epoch + 1}")
        tokenizer.save_pretrained(f"{OUTPUT_DIR}/checkpoint-{epoch + 1}")

    # 최종 저장
    print("\n💾 최종 모델 저장 중...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"🎉 학습 완료! 모델이 '{OUTPUT_DIR}' 폴더에 저장되었습니다.")


if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        print("❌ 학습 데이터 파일(train_style_data.txt)이 없습니다!")
    else:
        main()