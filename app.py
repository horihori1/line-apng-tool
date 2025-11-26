import streamlit as st
from PIL import Image, ImageDraw, ImageSequence
import io

# --- LINE広告 規定設定 ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20

# 【要件】
# 画像サイズ: 600x400
# 秒数: 4秒
# フレーム数: 20フレーム (1秒あたり5フレーム = 5fps)
# ループ数: 4回
# 容量: 300KB以下

# 計算: 1000ms / 5fps = 200ms (1フレームの表示時間)
FRAME_DURATION = 200 
TOTAL_FRAMES = 20
LOOP_COUNT = 4
MAX_FILE_SIZE_KB = 300 

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
    # フレーム数が20枚と多いため、300KBに収めるには減色が必須になる可能性が高いです
    # 画質の良い順に試行します (None=フルカラー -> 256色 -> 128色...)
    quality_steps = [None, 256, 128, 64, 32, 16]
    
    final_data = None
    used_colors = "Full Color"
    
    for colors in quality_steps:
        output_io = io.BytesIO()
        
        save_frames = []
        if colors is None:
            # フルカラー
            save_frames = frames
            mode_desc = "RGBA (フルカラー)"
        else:
            # 減色処理 (エラー回避のためデフォルトの量子化アルゴリズムを使用)
            for f in frames:
                converted = f.quantize(colors=colors)
                save_frames.append(converted)
            mode_desc = f"{colors}色"

        # APNG保存設定
        # duration=200ms, loop=4回
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
        
        # サイズ判定
        if size_kb <= target_kb:
            final_data = data
            used_colors = mode_desc
            break
        
    # もし最低画質でも300KBを超える場合、最も小さいサイズ(最後の試行結果)を返す
    if final_data is None:
        final_data = data
        used_colors = "規定超過 (これ以上圧縮できません)"

    return final_data, used_colors, len(final_data)/1024

def process_image(uploaded_file):
    original_img = Image.open(uploaded_file).convert("RGBA")
    
    # 1. 画像のリサイズ処理 (アスペクト比維持)
    # 背景透明の600x400キャンバスを作成
    base_img = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
    
    # 元画像をリサイズ（枠に収まるように）
    original_img.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    # 中央配置の座標計算
    x_offset = (TARGET_WIDTH - original_img.width) // 2
    y_offset = (TARGET_HEIGHT - original_img.height) // 2
    base_img.paste(original_img, (x_offset, y_offset), original_img)
    
    # 2. チェックマークの合成
    checkmark = create_checkmark_icon(CHECKMARK_SIZE)
    positions = [
        (MARGIN, MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, MARGIN),
        (MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN)
    ]
    
    # チェックありフレーム
    frame_with_checks = base_img.copy()
    for pos in positions:
        frame_with_checks.paste(checkmark, pos, checkmark)
        
    # チェックなしフレーム
    frame_no_checks = base_img.copy()
    
    # 3. 20フレーム分のシーケンス作成
    # 5fps (0.2秒間隔) で点滅させる
    raw_frames = []
    for i in range(TOTAL_FRAMES):
        if i % 2 == 0:
            raw_frames.append(frame_with_checks)
        else:
            raw_frames.append(frame_no_checks)
            
    # 4. 圧縮して出力
    return compress_to_target_size(raw_frames, MAX_FILE_SIZE_KB)

# --- UI ---

st.set_page_config(page_title="LINE Ads APNG Tool", layout="centered")

st.title("✅ LINE広告用 APNG生成")
st.caption("設定: 600x400px / 4秒 (20フレーム) / 4ループ / Max 300KB")

st.markdown("""
**LINE広告 アニメーション規定に準拠:**
* **画像サイズ**: 600px × 400px
* **再生時間**: 4秒 (200ms × 20フレーム)
* **ループ回数**: 4回
* **容量**: 300KB以下 (自動圧縮)
""")

uploaded_file = st.file_uploader("画像をアップロード (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("元画像")
        st.image(uploaded_file, use_column_width=True)

    with st.spinner("生成中... (フレーム数が多いため圧縮計算に少し時間がかかります)"):
        apng_bytes, used_colors, final_size_kb = process_image(uploaded_file)
    
    with col2:
        st.subheader("生成結果")
        st.image(apng_bytes, caption="プレビュー (0.2秒間隔点滅)", use_column_width=True)
        
        # 容量チェック結果の表示
        if final_size_kb <= MAX_FILE_SIZE_KB:
            st.success(f"✅ 容量: {final_size_kb:.1f} KB (OK)")
        else:
            st.error(f"⚠️ 容量: {final_size_kb:.1f} KB (規定超過 - 画像を単純にしてください)")
            
        st.info(f"画質設定: {used_colors}")

        st.download_button(
            label="LINE広告用APNGをダウンロード",
            data=apng_bytes,
            file_name="line_ads_4sec_20frames.png",
            mime="image/png"
        )
