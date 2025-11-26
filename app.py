import streamlit as st
from PIL import Image, ImageDraw
import io

# --- デフォルト設定（安全策） ---
# LINE規定: 600x400, 300KB以下
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20
MAX_FILE_SIZE_KB = 300 

def create_checkmark_icon(size):
    """チェックマーク描画"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    padding = 2
    draw.ellipse((padding, padding, size - padding, size - padding), fill=(0, 200, 0, 255))
    
    p1 = (size * 0.28, size * 0.50)
    p2 = (size * 0.45, size * 0.68)
    p3 = (size * 0.75, size * 0.35)
    draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=int(size * 0.12), joint="curve")
    return img

def compress_to_target_size(frames, target_kb, duration, loop_count):
    """容量圧縮ロジック"""
    # 画質優先度順
    quality_steps = [None, 256, 128, 64, 32, 16]
    final_data = None
    used_colors = "Full Color"
    
    for colors in quality_steps:
        output_io = io.BytesIO()
        
        save_frames = []
        if colors is None:
            save_frames = frames
            mode_desc = "RGBA (フルカラー)"
        else:
            for f in frames:
                converted = f.quantize(colors=colors)
                save_frames.append(converted)
            mode_desc = f"{colors}色"

        # loopパラメータ: Pillowでは「繰り返し回数」を指定します。
        # 0=無限, 1=1回繰り返し(計2回再生)... 
        # LINE規定に合わせて調整した値をセット
        save_frames[0].save(
            output_io,
            format="PNG",
            save_all=True,
            append_images=save_frames[1:],
            duration=duration,
            loop=loop_count, 
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
        used_colors = "規定超過"

    return final_data, used_colors, len(final_data)/1024

def process_image(uploaded_file, fps, total_frames, user_loop_setting):
    original_img = Image.open(uploaded_file).convert("RGBA")
    
    # 1. リサイズ
    base_img = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
    original_img.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    x = (TARGET_WIDTH - original_img.width) // 2
    y = (TARGET_HEIGHT - original_img.height) // 2
    base_img.paste(original_img, (x, y), original_img)
    
    # 2. チェックマーク
    checkmark = create_checkmark_icon(CHECKMARK_SIZE)
    positions = [
        (MARGIN, MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, MARGIN),
        (MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN),
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN)
    ]
    
    frame_with = base_img.copy()
    for pos in positions:
        frame_with.paste(checkmark, pos, checkmark)
    frame_no = base_img.copy()
    
    # 3. フレーム生成
    raw_frames = []
    for i in range(total_frames):
        if i % 2 == 0:
            raw_frames.append(frame_with)
        else:
            raw_frames.append(frame_no)
            
    # 4. パラメータ計算
    # ms単位の1フレーム表示時間
    duration_ms = int(1000 / fps)
    
    # Pillowのloop指定（繰り返し回数）
    # ユーザーが「4回」と言ったら、再生回数4回 = 初回 + 3回繰り返し なので -1 するのが安全
    # ただし、LINEの仕様によってはそのままの数字が良い場合もあるため、
    # ここでは「指定された回数分リピートさせる」設定にします。
    # UIで「3回」を選べば loop=3 (計4回再生) となるように調整推奨。
    
    return compress_to_target_size(raw_frames, MAX_FILE_SIZE_KB, duration_ms, user_loop_setting)

# --- UI ---
st.set_page_config(page_title="LINE Ads APNG Tool (Safe Mode)", layout="centered")

st.title("✅ LINE広告用 APNG生成（調整機能付）")
st.markdown("""
エラー回避のため、秒数とループ回数を微調整できます。
推奨設定は **「秒数: 3.8秒」「ループ設定: 3」** です。
""")

uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "png"])

if uploaded_file:
    st.markdown("---")
    
    # 設定用スライダーエリア
    st.subheader("⚙️ パラメータ調整")
    col_set1, col_set2 = st.columns(2)
    
    with col_set1:
        # 秒数調整: 20枚だと4.0秒ジャストでエラーになりやすいため、19枚(3.8秒)を推奨初期値に
        total_frames = st.slider("フレーム数 (秒数)", min_value=5, max_value=20, value=19, 
                                 help="19枚=3.8秒。20枚=4.0秒だとエラーになる場合があります。")
        fps = 5 # 固定
        
    with col_set2:
        # ループ設定: 4を指定すると「5回再生」とみなされエラーになる可能性があるため3を推奨
        loop_setting = st.slider("ループ回数設定 (Replays)", min_value=1, max_value=4, value=3,
                                 help="3を指定すると『初回再生＋3回繰り返し＝合計4回再生』になります。エラーが出る場合は減らしてください。")

    st.caption(f"現在の設定: 全{total_frames}フレーム / 約{total_frames/fps}秒 / ループ設定 {loop_setting}")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="元画像", use_column_width=True)

    if st.button("APNGを生成する"):
        with st.spinner("生成中..."):
            apng_bytes, used_colors, final_size_kb = process_image(uploaded_file, fps, total_frames, loop_setting)
        
        with col2:
            st.image(apng_bytes, caption=f"生成結果 ({used_colors})", use_column_width=True)
            
            if final_size_kb <= MAX_FILE_SIZE_KB:
                st.success(f"容量: {final_size_kb:.1f} KB (OK)")
            else:
                st.error(f"容量: {final_size_kb:.1f} KB (超過)")
                
            st.download_button(
                label="ダウンロード",
                data=apng_bytes,
                file_name="line_ads_safe.png",
                mime="image/png"
            )
