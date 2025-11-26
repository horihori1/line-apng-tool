import streamlit as st
from PIL import Image, ImageDraw
import io

# --- ページ設定 ---
st.set_page_config(page_title="LINE Ads APNG Tool (Auto)", layout="centered")

# --- 設定 (固定値) ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20
MAX_FILE_SIZE_KB = 300

# 【固定設定】
# 5フレーム (1秒) / 2ループ
FIXED_TOTAL_FRAMES = 5
FIXED_LOOP_COUNT = 2
FPS = 5
FRAME_DURATION_MS = int(1000 / FPS) # 200ms

def create_checkmark_icon(size):
    """チェックマーク画像を生成（背景透明）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 緑色の円
    padding = 2
    draw.ellipse((padding, padding, size - padding, size - padding), fill=(0, 200, 0, 255))
    
    # 白いチェックマーク
    p1
