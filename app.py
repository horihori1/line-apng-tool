import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 設定 (固定値) ---
# LINE規定: 600x400, 300KB以下
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20
MAX_FILE_SIZE_KB = 300

# 【固定設定】
# 10フレーム / 5fps = 2.0秒再生
# ループ2回
FIXED_TOTAL_FRAMES = 10
FIXED_LOOP_COUNT = 2
FPS = 5
FRAME_DURATION_MS = int(1000 / FPS) # 200ms

def create_checkmark_icon(size):
    """チェックマーク画像を生成（背景透明）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 緑色の円 (鮮やかな緑)
    padding = 2
    draw.ellipse((padding, padding, size - padding, size - padding), fill=(0, 200, 0, 255))
    
    # 白いチェックマーク
    p1 = (size * 0.28, size * 0.50)
    p2 = (size * 0.45, size * 0.68)
    p3 = (size * 0.75, size * 0.35)
    draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=int(size * 0.12), joint="curve")
    
    return img

def compress_to_target_size(frames):
    """
    【強化版】容量圧縮ロジック
    300KBに収まるまで、段階的に画質設定を下げて再生成を繰り返す
    """
