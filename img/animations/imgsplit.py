from PIL import Image
import os

# 스프라이트 시트 이미지 경로
SPRITE_PATH = "c:/Users/Owner/Documents/코딩/CSmonster/img/animations/스프라이트시트.png"
OUT_DIR = "c:/Users/Owner/Documents/코딩/CSmonster/img/animations/split_frames"
FRAME_WIDTH = 336
FRAME_HEIGHT = 190
FRAME_COUNT = 22

os.makedirs(OUT_DIR, exist_ok=True)

# 이미지 열기
sprite_sheet = Image.open(SPRITE_PATH)

for i in range(FRAME_COUNT):
    left = i * FRAME_WIDTH
    upper = 0
    right = left + FRAME_WIDTH
    lower = upper + FRAME_HEIGHT
    frame = sprite_sheet.crop((left, upper, right, lower))
    frame.save(os.path.join(OUT_DIR, f"{i}.png"))

print(f"{FRAME_COUNT}개의 프레임이 {OUT_DIR}에 저장되었습니다.")