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
    容量圧縮ロジック (フルカラー優先)
    設定が固定されたため、引数からdurationなどを削除し定数を使用
    """
    # 試行順序: フルカラー優先
    quality_steps = [None, 256, 128, 64, 32]
    
    final_data = None
    used_colors = "Full Color"
    
    for colors in quality_steps:
        output_io = io.BytesIO()
        
        save_frames = []
        if colors is None:
            # フルカラーモード (RGBA) - ここが最優先されます
            save_frames = frames
            mode_desc = "RGBA (フルカラー/元画像の色維持)"
        else:
            # 減色モード (容量削減のため)
            for f in frames:
                converted = f.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
                save_frames.append(converted)
            mode_desc = f"{colors}色 (減色圧縮)"

        # APNG保存 (固定値を使用)
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
        
        # 容量チェック: 規定内なら即採用して終了
        if size_kb <= MAX_FILE_SIZE_KB:
            final_data = data
            used_colors = mode_desc
            break
            
    # 規定オーバー時の最終手段
    if final_data is None:
        final_data = data
        used_colors = "規定超過"

    return final_data, used_colors, len(final_data)/1024

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
    
    # シーケンス作成 (10フレーム固定)
    raw_frames = []
    for i in range(FIXED_TOTAL_FRAMES):
        if i % 2 == 0:
            raw_frames.append(frame_with)
        else:
            raw_frames.append(frame_no)
            
    return compress_to_target_size(raw_frames)

# --- UI ---
st.set_page_config(page_title="LINE Ads APNG Tool (Fixed)", layout="centered")

st.title("✅ LINE広告用 APNG生成（設定固定版）")
st.markdown(f"""
以下の仕様で固定して生成します。色味は可能な限り維持されます。
* **画像サイズ**: 600x400 px
* **フレーム数**: {FIXED_TOTAL_FRAMES}枚 (約{FIXED_TOTAL_FRAMES/FPS:.1f}秒)
* **ループ回数**: {FIXED_LOOP_COUNT}回
* **容量**: 300KB以下 (自動調整)
""")

uploaded_file = st.file_uploader("画像をアップロード (JPG/PNG)", type=["jpg", "png"])

if uploaded_file:
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="元画像", use_column_width=True)

    if st.button("この画像でAPNGを生成する"):
        with st.spinner("生成中..."):
            # 引数を削除し、固定設定で処理
            apng_bytes, used_colors, final_size_kb = process_image(uploaded_file)
        
        with col2:
            st.image(apng_bytes, caption=f"生成結果 ({used_colors})", use_column_width=True)
            
            if final_size_kb <= MAX_FILE_SIZE_KB:
                st.success(f"容量: {final_size_kb:.1f} KB (OK)")
            else:
                st.error(f"容量: {final_size_kb:.1f} KB (超過)")
                
            st.download_button(
                label="ダウンロード",
                data=apng_bytes,
                file_name="line_ads_fixed_10frames.png",
                mime="image/png"
            )
