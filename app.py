import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 設定 ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20

# 【変更点】
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
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(
