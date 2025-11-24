import streamlit as st
from PIL import Image, ImageDraw, ImageOps
import io

# ==========================================
# LINE広告 (Small Image) 厳格仕様設定
# ==========================================
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
MAX_KB_SIZE = 300  # 300KB以下

def create_checkmark_icon(size):
    """緑の円＋白いチェックマークを描画"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 鮮やかな緑 (#00C853)
    padding = size * 0.05
    draw.ellipse([padding, padding, size - padding, size - padding], fill="#00C853", outline=None)
    
    # チェックマーク
    points = [(size * 0.28, size * 0.52), (size * 0.45, size * 0.70), (size * 0.75, size * 0.35)]
    stroke_width = int(size * 0.12)
    draw.line(points, fill="white", width=stroke_width, joint="curve")
    return img

def create_strict_line_apng(base_image, total_duration_sec, loop_count, total_frames, bg_color):
    """
    LINE広告仕様準拠 APNG生成 (パレット統一・完全エラー対策版)
    """
    # 1. 土台となるキャンバスを作成 (RGBA)
    canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), bg_color)
    
    # 2. 元画像をリサイズして中央に配置
    base_img = base_image.convert("RGBA")
    
    # 比率を維持したまま、枠に収まる最大サイズを計算
    base_img.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    # 中央位置を計算
    paste_x = (TARGET_WIDTH - base_img.width) // 2
    paste_y = (TARGET_HEIGHT - base_img.height) // 2
    
    # キャンバスに貼り付け
    canvas.paste(base_img, (paste_x, paste_y), base_img)
    
    # ベース画像をRGB(不透明)に統一
    final_base = canvas.convert("RGB")

    # 3. アイコン作成
    icon_size = int(TARGET_HEIGHT * 0.25)
    checkmark_icon = create_checkmark_icon(icon_size)
    margin = 20

    positions = [
        (margin, margin),                                      # 左上
        (TARGET_WIDTH - icon_size - margin, margin),           # 右上
        (margin, TARGET_HEIGHT - icon_size - margin),          # 左下
        (TARGET_WIDTH - icon_size - margin, TARGET_HEIGHT - icon_size - margin) # 右下
    ]

    # 4. フレーム生成
    # ONフレーム (チェックあり)
    frame_on = final_base.copy()
    for pos in positions:
        frame_on.paste(checkmark_icon, pos, checkmark_icon)
        
    # OFFフレーム (チェックなし)
    frame_off = final_base.copy()

    # ---【重要】パレット統一処理 ---
    # ここでエラー "images do not match" を防ぎます。
    # frame_on（色が一番多いコマ）を基準にして、パレット（色見本）を作成します。
    # method=2 (Fast Octree) を使用
    p_frame_on = frame_on.quantize(colors=256, method=2)
    
    # frame_off（色が少ないコマ）も、強制的に frame_on と同じパレットを使わせます。
    # これにより、データの構造が完全に一致し、エラーが消えます。
    p_frame_off = frame_off.quantize(palette=p_frame_on)

    frames = []
    
    # フレーム数を割り振り
    half_frames = total_frames // 2
    remainder = total_frames % 2
    
    # 前半 (ON) - パレット変換済みの画像を追加
    for _ in range(half_frames + remainder):
        frames.append(p_frame_on)
    # 後半 (OFF) - パレット変換済みの画像を追加
    for _ in range(half_frames):
        frames.append(p_frame_off)

    # 5. 保存処理
    duration_per_frame = int((total_duration_sec * 1000) / total_frames)
    output_io = io.BytesIO()
    
    # すでにquantize（軽量化）済みなので、そのまま保存します
    frames[0].save(
        output_io,
        format="PNG",
        save_all=True,
        append_images=frames[1:],
        duration=duration_per_frame,
        loop=loop_count,
        optimize=True,
        disposal=1
    )
    
    return output_io.getvalue()

# ==========================================
# UI部分
# ==========================================
st.set_page_config(page_title="LINE広告 APNG生成機", layout="centered")

st.title("LINE広告(Small) 完全対応版")
st.markdown("""
**特徴:**
* **どんな画像でもエラーが出ません** (パレット統一処理済み)
* 元画像の画角を維持します（余白を追加）
* フレーム数やループ数を細かく調整できます
""")

# サイドバー設定
st.sidebar.header("詳細設定")
duration = st.sidebar.slider("アニメーション秒数", 1.0, 4.0, 2.0, 0.5)
total_frames = st.sidebar.slider("フレーム数 (枚)", 5, 20, 10, 1)
loop_num = st.sidebar.slider("ループ回数", 1, 4, 0, 1)
bg_color_hex = st.sidebar.color_picker("余白の色
                                       
