import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 設定 ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20

# 【変更点】
# 10フレームで最大4秒の制限を守るため、0.4秒(400ms)間隔に設定
# 400ms * 10frames = 4000ms (4.0秒)
FRAME_DURATION = 400 
TOTAL_FRAMES = 10
MAX_FILE_SIZE_KB = 300
LOOP_COUNT = 3  # ループ回数指定

def create_checkmark_icon(size):
    """
    PILを使って緑色の円と白いチェックマークを描画し、RGBA画像を返す
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 緑色の円
    padding = 2
    draw.ellipse(
        (padding, padding, size - padding, size - padding),
        fill=(0, 200, 0, 255),
        outline=None
    )

    # 白いチェックマーク
    p1 = (size * 0.28, size * 0.50)
    p2 = (size * 0.45, size * 0.68)
    p3 = (size * 0.75, size * 0.35)
    draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=int(size * 0.12), joint="curve")

    return img

def
