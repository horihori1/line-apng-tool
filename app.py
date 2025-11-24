import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 設定 ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20

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
    
    # 線の描画（引数が長いため改行して記述）
    draw.line(
        [p1, p2, p3], 
        fill=(255, 255, 255, 255), 
        width=int(size * 0.12), 
        joint="curve"
    )

    return img

def compress_to_target_size(frames, target_kb):
    """
    指定されたファイルサイズ以下になるまで、色数を減らしながらAPNGを生成する
    """
    quality_steps = [None, 256, 128, 64, 32]
    
    final_data = None
    used_colors = "Full Color"
    
    for colors in quality_steps:
        output_io = io.BytesIO()
        
        if colors is None:
            save_frames = frames
            mode_desc = "RGBA (フルカラー)"
        else:
            # 減色処理
            save_frames = []
            for f in frames:
                # quantizeメソッドを使用
                converted = f.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
                save_frames.append(converted)
            mode_desc = f"{colors}色"

        # 保存処理
        save_frames[0].save(
            output_io,
            format="PNG",
            save_all=True,
            append_images=save_frames[1:],
            duration=FRAME_DURATION,
            loop=LOOP_COUNT,
            optimize=True
        )
        
        data = output_io.getvalue()
        size_kb = len(data) / 1024
        
        if size_kb <= target_kb:
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
    
    # 10フレーム分のシーケンス作成
    raw_frames = []
    for i in range(TOTAL_FRAMES):
        if i % 2 == 0:
            raw_frames.append(frame_with_checks)
        else:
            raw_frames.append(frame_no_checks)
            
    return compress_to_target_size(raw_frames, MAX_FILE_SIZE_KB)

# --- UI ---

st.set_page_config(page_title="APNG Generator (Final)", layout="centered")

st.title("✅ 四隅チェックマーク APNG生成")
st.caption("仕様固定版: 10フレーム / 4秒 / 3回ループ / Max 300KB")

st.markdown(f"""
* **画像サイズ**: {TARGET_WIDTH}x{TARGET_HEIGHT}
* **フレーム数**: {TOTAL_FRAMES}枚 (0.4秒間隔)
* **再生時間**: {TOTAL_FRAMES * FRAME_DURATION / 1000:.1f}秒
* **ループ**: {LOOP_COUNT}回
* **容量**: 300KB以下自動調整
""")

uploaded_file = st.file_uploader("画像をアップロード (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("元画像")
        st.image(uploaded_file, use_column_width=True)

    with st.spinner("生成中..."):
        apng_bytes, used_colors, final_size_kb = process_image(uploaded_file)
    
    with col2:
        st.subheader("生成結果")
        st.image(apng_bytes, caption="プレビュー", use_column_width=True)
        
        if final_size_kb <= MAX_FILE_SIZE_KB:
            st.success(f"✅ 容量: {final_size_kb:.1f} KB (OK)")
        else:
            st.error(f"⚠️ 容量: {final_size_kb:.1f} KB (300KBを超過)")
            
        st.info(f"画質: {used_colors}")

        st.download_button(
            label="APNGをダウンロード",
            data=apng_bytes,
            file_name="checked_anim_fixed.png",
            mime="image/png"
        )
