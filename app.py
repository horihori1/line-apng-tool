import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 設定（LINE広告用） ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20

# 規定: 最短1秒〜最長4秒 / フレーム5〜20
# 設定: 10フレーム / 0.3秒間隔 = 合計3.0秒
FRAME_DURATION = 300 
TOTAL_FRAMES = 10
MAX_FILE_SIZE_KB = 300 # 最大300KB
LOOP_COUNT = 3         # 規定: 1〜4回

def create_checkmark_icon(size):
    """チェックマーク画像を作成"""
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

def compress_to_target_size(frames, target_kb):
    """
    指定サイズ以下になるまで色数を減らして圧縮する
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
            save_frames = []
            for f in frames:
                # 【修正箇所】エラーの原因となる method指定 を削除し、デフォルト(FastOctree)を使用
                converted = f.quantize(colors=colors)
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
        
        # 容量チェック
        if size_kb <= target_kb:
            final_data = data
            used_colors = mode_desc
            break
            
    # もし32色でもオーバーする場合は、最後の結果を返す
    if final_data is None:
        final_data = data
        used_colors = "32色 (サイズ超過)"

    return final_data, used_colors, len(final_data)/1024

def process_image(uploaded_file):
    original_img = Image.open(uploaded_file).convert("RGBA")
    
    # 1. 600x400のキャンバスを作成（背景透明）
    base_img = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
    
    # 2. アスペクト比を維持してリサイズし、中央に配置
    # (画像を歪ませないための処理です)
    original_img.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    x_offset = (TARGET_WIDTH - original_img.width) // 2
    y_offset = (TARGET_HEIGHT - original_img.height) // 2
    base_img.paste(original_img, (x_offset, y_offset), original_img)
    
    # 3. チェックマーク素材作成
    checkmark = create_checkmark_icon(CHECKMARK_SIZE)
    positions = [
        (MARGIN, MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, MARGIN),
        (MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN)
    ]
    
    # 4. フレーム画像の作成
    frame_with_checks = base_img.copy()
    for pos in positions:
        frame_with_checks.paste(checkmark, pos, checkmark)
    frame_no_checks = base_img.copy()
    
    # 5. アニメーションシーケンス作成 (10フレーム)
    raw_frames = []
    for i in range(TOTAL_FRAMES):
        if i % 2 == 0:
            raw_frames.append(frame_with_checks)
        else:
            raw_frames.append(frame_no_checks)
            
    return compress_to_target_size(raw_frames, MAX_FILE_SIZE_KB)

# --- UI ---
st.set_page_config(page_title="LINE Ads APNG Generator", layout="centered")
st.title("✅ LINE広告用 APNG生成")
st.caption("仕様: 600x400px / 3秒 / 3回ループ / Max 300KB")

uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "png"])

if uploaded_file:
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("元画像")
        st.image(uploaded_file, use_column_width=True)
    
    with st.spinner("処理中..."):
        apng_bytes, used_colors, final_size_kb = process_image(uploaded_file)
    
    with col2:
        st.subheader("生成結果 (600x400)")
        st.image(apng_bytes, caption="プレビュー", use_column_width=True)
        
        if final_size_kb <= MAX_FILE_SIZE_KB:
            st.success(f"容量: {final_size_kb:.1f} KB (OK)")
        else:
            st.error(f"容量: {final_size_kb:.1f} KB (規定超過)")
        
        st.info(f"画質: {used_colors}")
        
        st.download_button(
            label="ダウンロード",
            data=apng_bytes,
            file_name="line_ads_600x400.png",
            mime="image/png"
        )
