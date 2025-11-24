import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 設定 ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20

# 10フレームで合計3秒にするため、1フレーム0.3秒(300ms)に設定
# 300ms * 10frames = 3000ms (3.0秒)
FRAME_DURATION = 300 
TOTAL_FRAMES = 10
MAX_FILE_SIZE_KB = 300
LOOP_COUNT = 3  # ループ回数指定

def create_checkmark_icon(size):
    """
    PILを使って緑色の円と白いチェックマークを描画し、RGBA画像を返す
    """
    # 背景透明のキャンバス作成
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    
    # 描画オブジェクト
    draw = ImageDraw.Draw(img)

    # 緑色の円
    padding = 2
    draw.ellipse(
        (padding, padding, size - padding, size - padding),
        fill=(0, 200, 0, 255),
        outline=None
    )

    # 白いチェックマークの座標
    p1 = (size * 0.28, size * 0.50)
    p2 = (size * 0.45, size * 0.68)
    p3 = (size * 0.75, size * 0.35)
    
    # 線の描画
    draw.line(
        [p
