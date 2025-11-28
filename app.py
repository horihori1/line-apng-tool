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
    p1 = (size * 0.28, size * 0.50)
    p2 = (size * 0.45, size * 0.68)
    p3 = (size * 0.75, size * 0.35)
    draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=int(size * 0.12), joint="curve")
    
    return img

def save_as_full_color(frames):
    """
    【フルカラー固定】保存ロジック
    減色処理を一切行わず、画質を維持したまま保存する。
    """
    output_io = io.BytesIO()
    
    frames[0].save(
        output_io,
        format="PNG",
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=FIXED_LOOP_COUNT,
        optimize=True
    )
    
    data = output_io.getvalue()
    size_kb = len(data) / 1024
    
    return data, size_kb

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
    raw_frames = []
    for i in range(FIXED_TOTAL_FRAMES):
        if i % 2 == 0:
            raw_frames.append(frame_with)
        else:
            raw_frames.append(frame_no)
            
    return save_as_full_color(raw_frames)

# --- UI ---

st.title("✅ LINE広告用 APNG生成")
st.caption("アップロード後、即時生成します（フルカラー / 5フレーム / 2ループ）")

uploaded_file = st.file_uploader("画像をアップロード (JPG/PNG)", type=["jpg", "png"])

if uploaded_file:
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("元画像")
        st.image(uploaded_file, use_column_width=True)

    # アップロードされたら自動的に処理を開始
    with st.spinner("自動生成中..."):
        apng_bytes, final_size_kb = process_image(uploaded_file)
    
    with col2:
        st.subheader("生成結果")
        st.image(apng_bytes, caption="フルカラー生成結果", use_column_width=True)
        
        # 容量判定
        if final_size_kb <= MAX_FILE_SIZE_KB:
            st.success(f"✅ 容量: {final_size_kb:.1f} KB (OK)")
        else:
            st.error(f"⚠️ 容量: {final_size_kb:.1f} KB (規定超過)")
            st.caption("色味維持のため圧縮していません。")
            
        # ダウンロードボタン
        st.download_button(
            label="ダウンロード",
            data=apng_bytes,
            file_name="line_ads_5frames_2loop.png",
            mime="image/png",
            type="primary"
        )
