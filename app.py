import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 設定 ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20
FRAME_DURATION = 500  # ms
TOTAL_FRAMES = 6      # 3秒分 (要件: 5～20フレーム)
MAX_FILE_SIZE_KB = 300  # 上限300KB

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

def compress_to_target_size(frames, target_kb):
    """
    指定されたファイルサイズ以下になるまで、色数を減らしながらAPNGを生成する
    """
    # 試行する色数のリスト (NoneはフルカラーRGBA, それ以外はPモードで減色)
    # 画質の良い順に試す
    quality_steps = [None, 256, 128, 64, 32]
    
    final_data = None
    used_colors = "Full Color"
    
    for colors in quality_steps:
        output_io = io.BytesIO()
        
        # フレームの準備（減色処理）
        if colors is None:
            # フルカラー (RGBA)
            save_frames = frames
            mode_desc = "RGBA (フルカラー)"
        else:
            # 減色 (Pモード + ディザリング)
            # quantizeメソッドでパレット画像に変換することで劇的にサイズが落ちます
            save_
