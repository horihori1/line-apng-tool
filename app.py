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
            save_frames = [f.quantize(colors=colors, method=Image.Quantize.MEDIANCUT) for f in frames]
            mode_desc = f"{colors}色"

        # APNG保存
        save_frames[0].save(
            output_io,
            format="PNG",
            save_all=True,
            append_images=save_frames[1:],
            duration=FRAME_DURATION,
            loop=0,
            optimize=True
        )
        
        data = output_io.getvalue()
        size_kb = len(data) / 1024
        
        # サイズ判定
        if size_kb <= target_kb:
            final_data = data
            used_colors = mode_desc
            break
        
    # ループを抜けてもfinal_dataがない場合（32色でも300KB超えの場合）、
    # 最も圧縮率の高かった最後(32色)のデータを返す
    if final_data is None:
        final_data = data
        used_colors = "32色 (サイズ超過)"

    return final_data, used_colors, len(final_data)/1024

def process_image(uploaded_file):
    """
    画像を読み込み、合成し、圧縮処理を経てAPNGを返す
    """
    original_img = Image.open(uploaded_file).convert("RGBA")
    
    # 1. リサイズ
    base_img = original_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    # 2. 合成用素材作成
    checkmark = create_checkmark_icon(CHECKMARK_SIZE)
    positions = [
        (MARGIN, MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, MARGIN),
        (MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN)
    ]
    
    # 3. フレーム作成 (ON/OFF)
    frame_with_checks = base_img.copy()
    for pos in positions:
        frame_with_checks.paste(checkmark, pos, checkmark)
    frame_no_checks = base_img.copy()
    
    # 4. シーケンス作成 (6フレーム)
    raw_frames = []
    for i in range(TOTAL_FRAMES):
        if i % 2 == 0:
            raw_frames.append(frame_with_checks)
        else:
            raw_frames.append(frame_no_checks)
            
    # 5. サイズ圧縮処理を実行
    return compress_to_target_size(raw_frames, MAX_FILE_SIZE_KB)

# --- UI ---

st.set_page_config(page_title="APNG Generator (Under 300KB)", layout="centered")

st.title("✅ 四隅チェックマーク APNG生成")
st.caption("自動圧縮機能付き (Max 300KB)")

st.markdown(f"""
以下の仕様でアニメーション画像を生成します。
* **サイズ**: {TARGET_WIDTH}x{TARGET_HEIGHT}
* **仕様**: {TOTAL_FRAMES}フレーム / {TOTAL_FRAMES * FRAME_DURATION / 1000}秒
* **容量**: **300KB以下になるよう自動調整**
""")

uploaded_file = st.file_uploader("画像をアップロード (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("元画像")
        st.image(uploaded_file, use_column_width=True)

    with st.spinner("生成と圧縮処理中..."):
        apng_bytes, used_colors, final_size_kb = process_image(uploaded_file)
    
    with col2:
        st.subheader("生成結果")
        st.image(apng_bytes, caption="プレビュー", use_column_width=True)
        
        # サイズ情報の表示（色分け）
        if final_size_kb <= MAX_FILE_SIZE_KB:
            st.success(f"✅ 容量: {final_size_kb:.1f} KB (OK)")
        else:
            st.error(f"⚠️ 容量: {final_size_kb:.1f} KB (300KBを超過)")
            
        st.info(f"適用された画質: **{used_colors}**")

        st.download_button(
            label="APNGをダウンロード",
            data=apng_bytes,
            file_name="checked_anim_300kb.png",
            mime="image/png"
        )
        
