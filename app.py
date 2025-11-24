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
    LINE広告仕様準拠 APNG生成
    """
    # 1. 画像のリサイズ (画角維持・余白追加)
    base_img = base_image.convert("RGBA")
    
    # 元の比率を維持してリサイズし、足りない部分は指定色(白など)で埋める
    # centering=(0.5, 0.5) で中央寄せ
    base_img = ImageOps.pad(
        base_img, 
        (TARGET_WIDTH, TARGET_HEIGHT), 
        method=Image.Resampling.LANCZOS, 
        color=bg_color, 
        centering=(0.5, 0.5)
    )

    # 2. アイコン作成
    icon_size = int(TARGET_HEIGHT * 0.25) # 高さの25% (約100px)
    checkmark_icon = create_checkmark_icon(icon_size)
    margin = 20

    positions = [
        (margin, margin),                                      # 左上
        (TARGET_WIDTH - icon_size - margin, margin),           # 右上
        (margin, TARGET_HEIGHT - icon_size - margin),          # 左下
        (TARGET_WIDTH - icon_size - margin, TARGET_HEIGHT - icon_size - margin) # 右下
    ]

    # 3. フレーム生成 (ON/OFF切り替え)
    frame_on = base_img.copy()
    for pos in positions:
        frame_on.paste(checkmark_icon, pos, checkmark_icon)
    
    frame_off = base_img.copy()

    frames = []
    
    # 指定されたフレーム数を半分ずつ ON / OFF に割り振る
    half_frames = total_frames // 2
    remainder = total_frames % 2 # 奇数の場合の端数
    
    # 前半 (ON)
    for _ in range(half_frames + remainder):
        frames.append(frame_on)
    # 後半 (OFF)
    for _ in range(half_frames):
        frames.append(frame_off)

    # 4. 1フレームあたりの表示時間を計算
    duration_per_frame = int((total_duration_sec * 1000) / total_frames)

    # 5. 保存
    output_io = io.BytesIO()
    
    # method=2 (Fast Octree) で減色処理を行い容量を削減
    frames_quantized = [f.quantize(colors=256, method=2) for f in frames]

    frames_quantized[0].save(
        output_io,
        format="PNG",
        save_all=True,
        append_images=frames_quantized[1:],
        duration=duration_per_frame,
        loop=loop_count,
        optimize=True,
        disposal=1 # 背景をクリアせずに上書きする設定(ちらつき防止)
    )
    
    return output_io.getvalue()

# ==========================================
# UI部分
# ==========================================
st.set_page_config(page_title="LINE広告 APNG生成機", layout="centered")

st.title("LINE広告(Small) 完全対応版")
st.markdown("""
**特徴:**
* 元画像の画角を維持します（余白を追加）
* フレーム数やループ数を細かく調整できます
* 容量オーバーしないよう自動圧縮します
""")

# サイドバー設定
st.sidebar.header("詳細設定")

# 秒数設定
duration = st.sidebar.slider("アニメーション秒数", 1.0, 4.0, 2.0, 0.5, help="仕様: 最短1秒、最長4秒")

# フレーム数設定 (ユーザー調整可能に)
total_frames = st.sidebar.slider("フレーム数 (枚)", 5, 20, 10, 1, help="仕様: 5枚～20枚。多いほど滑らかですが容量が増えます。")

# ループ数設定
loop_num = st.sidebar.slider("ループ回数", 1, 4, 0, 1, help="仕様: 1～4回 (0にすると無限ループになりますが審査落ちします)")

# 背景色設定 (余白の色)
bg_color_hex = st.sidebar.color_picker("余白の色 (背景色)", "#FFFFFF")


uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("元画像")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("プレビュー")
        if st.button("変換・生成する", type="primary"):
            with st.spinner("生成中..."):
                try:
                    # 生成処理
                    apng_data = create_strict_line_apng(
                        image, 
                        duration, 
                        loop_num, 
                        total_frames, 
                        bg_color_hex
                    )
                    
                    # 容量チェック
                    kb_size = len(apng_data) / 1024
                    st.image(apng_data, use_container_width=True)
                    
                    st.markdown(f"**仕上がり: {kb_size:.1f}KB / {total_frames}フレーム**")
                    
                    if kb_size <= 300:
                        st.success("✅ 審査基準OK")
                    else:
                        st.warning("⚠️ 300KBを超えました。フレーム数を減らすか、秒数を短くしてください。")

                    # ファイル名生成
                    file_name = f"line_{total_frames}frames_{int(duration)}s.png"
                    
                    st.download_button(
                        label="📥 APNGをダウンロード",
                        data=apng_data,
                        file_name=file_name,
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"エラー: {e}")
                    
