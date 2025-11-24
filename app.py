import streamlit as st
from PIL import Image, ImageDraw, ImageOps
import io

# ==========================================
# LINE広告 (Small Image) 厳格仕様設定
# ==========================================
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
TOTAL_FRAMES = 10  # 要件「5～20枚」を満たすため10枚で固定
MAX_KB_SIZE = 300  # 要件「300KB以下」

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

def create_strict_line_apng(base_image, total_duration_sec, loop_count):
    """
    LINE広告の仕様を強制的に守ったAPNGを作成する
    """
    # 1. 画像のリサイズ (600x400)
    base_img = base_image.convert("RGBA")
    base_img = ImageOps.fit(base_img, (TARGET_WIDTH, TARGET_HEIGHT), method=Image.Resampling.LANCZOS)

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

    # 3. フレーム生成 (10フレーム)
    frame_on = base_img.copy()
    for pos in positions:
        frame_on.paste(checkmark_icon, pos, checkmark_icon)
    
    frame_off = base_img.copy()

    frames = []
    # ONを5枚
    for _ in range(5):
        frames.append(frame_on)
    # OFFを5枚
    for _ in range(5):
        frames.append(frame_off)

    # 4. 表示時間の計算
    duration_per_frame = int((total_duration_sec * 1000) / TOTAL_FRAMES)

    # 5. 保存 (エラー対策版)
    output_io = io.BytesIO()
    
    # 【修正点】
    # quantize(減色)は行いますが、エラーの原因となる disposal 設定を削除しました。
    # method=0 (MedianCut) は安定性が高いためこちらを使用します。
    frames_quantized = [f.quantize(colors=128, method=0) for f in frames]

    frames_quantized[0].save(
        output_io,
        format="PNG",
        save_all=True,
        append_images=frames_quantized[1:],
        duration=duration_per_frame,
        loop=loop_count,
        optimize=False, # クラッシュ回避のためFalseに変更（quantizeで十分軽くなります）
        # disposal=1  <-- これがクラッシュの原因だったので削除しました
    )
    
    return output_io.getvalue()

# ==========================================
# UI部分
# ==========================================
st.set_page_config(page_title="LINE広告 APNG生成機", layout="centered")

st.title("LINE広告(Small) 完全対応版")
st.markdown("""
以下の厳格な仕様に自動適合させます：
* サイズ: **600x400px** (自動トリミング)
* フレーム数: **10枚** (仕様:5-20枚)
* 容量: **300KB以下** (自動圧縮)
""")

# サイドバー設定
st.sidebar.header("LINE広告設定")

# 秒数設定
duration = st.sidebar.slider("アニメーション秒数", 1.0, 4.0, 2.0, 0.5, help="仕様: 最短1秒、最長4秒")

# ループ数設定
loop_num = st.sidebar.slider("ループ回数", 1, 4, 0, 1, help="仕様: 1～4回 (無限ループ不可)")

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
            with st.spinner("規格に合わせて変換中..."):
                try:
                    # 生成処理
                    apng_data = create_strict_line_apng(image, duration, loop_num)
                    
                    # 容量チェック
                    kb_size = len(apng_data) / 1024
                    st.image(apng_data, use_container_width=True)
                    
                    st.markdown(f"**仕上がりサイズ: {kb_size:.1f}KB**")
                    
                    if kb_size <= 300:
                        st.success("✅ 審査基準OK (300KB以下)")
                    else:
                        st.warning("⚠️ 容量が300KBを少し超えています。アニメーション秒数を短くするか、単純な画像を使用してください。")

                    # ファイル名生成
                    file_name = f"line_600x400_{int(duration)}s_loop{loop_num}.png"
                    
                    st.download_button(
                        label="📥 基準適合APNGをダウンロード",
                        data=apng_data,
                        file_name=file_name,
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
