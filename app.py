import streamlit as st
from PIL import Image, ImageDraw
import io

# --- ページ設定 ---
st.set_page_config(page_title="LINE Ads APNG Tool", layout="centered")

# --- 設定 (固定値) ---
# LINE規定: 600x400, 300KB以下
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20
MAX_FILE_SIZE_KB = 300

# 【今回の変更点】
# 5フレーム (1秒)
# 2ループ
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
    p1 = (size * 0.28, size * 0.50)
    p2 = (size * 0.45, size * 0.68)
    p3 = (size * 0.75, size * 0.35)
    draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=int(size * 0.12), joint="curve")
    
    return img

def compress_to_target_size(frames):
    """
    容量圧縮ロジック (安全版)
    """
    # 圧縮レベル設定
    compression_levels = [
        {"colors": None, "label": "最高画質 (フルカラー)"},
        {"colors": 256, "label": "高画質 (256色)"},
        {"colors": 128, "label": "中画質 (128色)"},
        {"colors": 64,  "label": "圧縮 (64色)"},
        {"colors": 32,  "label": "強力圧縮 (32色)"},
        {"colors": 16,  "label": "最大圧縮 (16色)"}
    ]
    
    final_data = None
    used_setting = ""
    
    for setting in compression_levels:
        output_io = io.BytesIO()
        save_frames = []
        
        if setting["colors"] is None:
            # フルカラー
            save_frames = frames
        else:
            # 減色処理 (エラー回避のためシンプルな記述)
            for f in frames:
                converted = f.quantize(colors=setting["colors"])
                save_frames.append(converted)

        # APNG保存
        save_frames[0].save(
            output_io,
            format="PNG",
            save_all=True,
            append_images=save_frames[1:],
            duration=FRAME_DURATION_MS,
            loop=FIXED_LOOP_COUNT,
            optimize=True
        )
        
        data = output_io.getvalue()
        size_kb = len(data) / 1024
        
        # 300KB以下なら採用
        if size_kb <= MAX_FILE_SIZE_KB:
            final_data = data
            used_setting = setting["label"]
            break
            
    if final_data is None:
        final_data = data
        used_setting = "規定超過"

    return final_data, used_setting, len(final_data)/1024

def process_image(uploaded_file):
    original_img = Image.open(uploaded_file).convert("RGBA")
    
    # 1. ベース画像の作成
    base_img = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
    original_img.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    x = (TARGET_WIDTH - original_img.width) // 2
    y = (TARGET_HEIGHT - original_img.height) // 2
    base_img.paste(original_img, (x, y), original_img)
    
    # 2. チェックマーク画像の作成
    checkmark = create_checkmark_icon(CHECKMARK_SIZE)
    positions = [
        (MARGIN, MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, MARGIN),
        (MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN)
    ]
    
    # 3. フレームの作成
    frame_with = base_img.copy()
    for pos in positions:
        frame_with.paste(checkmark, pos, checkmark)
    frame_no = base_img.copy()
    
    # シーケンス作成 (5フレーム)
    # 0:ON, 1:OFF, 2:ON, 3:OFF, 4:ON
    raw_frames = []
    for i in range(FIXED_TOTAL_FRAMES):
        if i % 2 == 0:
            raw_frames.append(frame_with)
        else:
            raw_frames.append(frame_no)
            
    return compress_to_target_size(raw_frames)

# --- UI ---

st.title("✅ LINE広告用 APNG生成")
st.markdown(f"""
以下の仕様で生成し、**300KB以下になるよう自動で圧縮**します。
* **画像サイズ**: 600x400 px
* **フレーム数**: {FIXED_TOTAL_FRAMES}枚 (1秒)
* **ループ回数**: {FIXED_LOOP_COUNT}回
""")

uploaded_file = st.file_uploader("画像をアップロード (JPG/PNG)", type=["jpg", "png"])

if uploaded_file:
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="元画像", use_column_width=True)

    if st.button("生成する"):
        with st.spinner("生成中..."):
            apng_bytes, used_setting, final_size_kb = process_image(uploaded_file)
        
        with col2:
            st.image(apng_bytes, caption=f"生成結果: {used_setting}", use_column_width=True)
            
            if final_size_kb <= MAX_FILE_SIZE_KB:
                st.success(f"容量: {final_size_kb:.1f} KB (OK)")
            else:
                st.error(f"容量: {final_size_kb:.1f} KB (超過)")
                
            st.download_button(
                label="ダウンロード",
                data=apng_bytes,
                file_name="line_ads_5frames.png",
                mime="image/png"
            )
