import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 設定 ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20
FRAME_DURATION = 300   # 0.3秒
TOTAL_FRAMES = 10      # 10枚 (計3.0秒)
MAX_FILE_SIZE_KB = 300
LOOP_COUNT = 3         # 3回ループ

def create_checkmark_icon(size):
    """チェックマーク画像を作成"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 円とチェックマークを描画（コピーミスを防ぐため1行にまとめました）
    padding = 2
    draw.ellipse((padding, padding, size - padding, size - padding), fill=(0, 200, 0, 255))
    
    p1 = (size * 0.28, size * 0.50)
    p2 = (size * 0.45, size * 0.68)
    p3 = (size * 0.75, size * 0.35)
    draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=int(size * 0.12), joint="curve")
    
    return img

def compress_to_target_size(frames, target_kb):
    """容量圧縮ロジック"""
    quality_steps = [None, 256, 128, 64, 32]
    final_data = None
    used_colors = "Full Color"
    
    for colors in quality_steps:
        output_io = io.BytesIO()
        if colors is None:
            save_frames = frames
            mode_desc = "RGBA (フルカラー)"
        else:
            save_frames = [f.quantize(colors=colors, method=Image.Quantize.MEDIANCUT) for f in frames]
            mode_desc = f"{colors}色"

        # 保存設定
        save_frames[0].save(output_io, format="PNG", save_all=True, append_images=save_frames[1:], duration=FRAME_DURATION, loop=LOOP_COUNT, optimize=True)
        
        data = output_io.getvalue()
        if (len(data) / 1024) <= target_kb:
            final_data = data
            used_colors = mode_desc
            break
            
    if final_data is None:
        final_data = data
        used_colors = "32色 (サイズ超過)"

    return final_data, used_colors, len(final_data)/1024

def process_image(uploaded_file):
    original_img = Image.open(uploaded_file).convert("RGBA")
    base_img = original_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    checkmark = create_checkmark_icon(CHECKMARK_SIZE)
    
    positions = [
        (MARGIN, MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, MARGIN),
        (MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN)
    ]
    
    frame_with_checks = base_img.copy()
    for pos in positions:
        frame_with_checks.paste(checkmark, pos, checkmark)
    frame_no_checks = base_img.copy()
    
    raw_frames = []
    for i in range(TOTAL_FRAMES):
        if i % 2 == 0:
            raw_frames.append(frame_with_checks)
        else:
            raw_frames.append(frame_no_checks)
            
    return compress_to_target_size
