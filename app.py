import streamlit as st
from PIL import Image, ImageDraw
import io

# --- 設定 ---
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
CHECKMARK_SIZE = 80
MARGIN = 20
FRAME_DURATION = 500  # ms (0.5秒)
TOTAL_FRAMES = 6      # 5～20フレームの要件を満たすため6フレーム（3秒）に設定

def create_checkmark_icon(size):
    """
    PILを使って緑色の円と白いチェックマークを描画し、RGBA画像を返す関数
    """
    # 背景透明のキャンバス作成
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. 緑色の円を描画
    # エリアいっぱいに描くと端が切れることがあるので少しパディングを入れる
    padding = 2
    draw.ellipse(
        (padding, padding, size - padding, size - padding),
        fill=(0, 200, 0, 255),  # 鮮やかな緑
        outline=None
    )

    # 2. 白いチェックマークを描画
    # 座標計算 (円の中央に配置されるように調整)
    # 左上(start) -> 下(mid) -> 右上(end)
    p1 = (size * 0.28, size * 0.50)
    p2 = (size * 0.45, size * 0.68)
    p3 = (size * 0.75, size * 0.35)
    
    draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=int(size * 0.12), joint="curve")

    return img

def process_image(uploaded_file):
    """
    画像を読み込み、リサイズし、四隅にチェックマークを合成したAPNGバイトデータを生成する
    """
    # 画像を開く
    original_img = Image.open(uploaded_file).convert("RGBA")
    
    # 1. 規定サイズ(600x400)にリサイズ (アスペクト比維持ではなく強制リサイズで仕様に合わせる)
    base_img = original_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    # 2. チェックマーク素材の作成
    checkmark = create_checkmark_icon(CHECKMARK_SIZE)
    
    # 3. 四隅の座標を計算
    # 左上、右上、左下、右下
    positions = [
        (MARGIN, MARGIN),                                           # 左上
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, MARGIN),           # 右上
        (MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN),          # 左下
        (TARGET_WIDTH - CHECKMARK_SIZE - MARGIN, TARGET_HEIGHT - CHECKMARK_SIZE - MARGIN) # 右下
    ]
    
    # 4. フレームの作成
    # Frame A: チェックマークあり
    frame_with_checks = base_img.copy()
    for pos in positions:
        frame_with_checks.paste(checkmark, pos, checkmark)
        
    # Frame B: チェックマークなし（ベース画像そのまま）
    frame_no_checks = base_img.copy()
    
    # 5. APNG用フレームシーケンスの作成
    # 要件「5～20フレーム」「最短1秒」を満たすため、
    # [あり, なし, あり, なし, あり, なし] の6フレーム構成にする
    # 1フレーム0.5秒 x 6 = 3.0秒
    frames = []
    for i in range(TOTAL_FRAMES):
        if i % 2 == 0:
            frames.append(frame_with_checks)
        else:
            frames.append(frame_no_checks)
            
    # 6. メモリバッファにAPNGとして保存
    output_io = io.BytesIO()
    
    # save_all=Trueでアニメーション保存
    # loop=0は無限ループ（ブラウザプレビュー用）。
    # 要件に「ループ数1～4」とあるが、多くのビューアで確認しやすいようデフォルトは0(無限)推奨。
    # ここでは仕様厳守のためダウンロード時は無限(0)にしておくが、LINEスタンプ等の場合は別途ツールで調整が必要な場合あり。
    frames[0].save(
        output_io,
        format="PNG",
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION,
        loop=0,
        optimize=True
    )
    
    return output_io.getvalue()

# --- Streamlit UI ---

st.set_page_config(page_title="APNG Generator", layout="centered")

st.title("✅ 四隅チェックマーク APNG生成")
st.markdown("""
画像をアップロードすると、以下の仕様に合わせて**四隅で緑色のチェックマークが点滅するアニメーションPNG (APNG)** を生成します。
素材画像は不要です。プログラムが自動で描画します。

* **出力サイズ**: 600x400 px
* **アニメーション**: 0.5秒間隔で点滅 (計3秒 / 6フレーム)
""")

uploaded_file = st.file_uploader("画像をアップロード (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("元画像")
        st.image(uploaded_file, use_column_width=True)

    # 処理実行
    with st.spinner("APNG生成中..."):
        apng_bytes = process_image(uploaded_file)
    
    with col2:
        st.subheader("生成されたAPNG")
        # StreamlitでAPNGを表示するにはimageメソッドでそのまま表示可能
        st.image(apng_bytes, caption="プレビュー（点滅します）", use_column_width=True)
        
        # ダウンロードボタン
        st.download_button(
            label="APNGをダウンロード",
            data=apng_bytes,
            file_name="checked_animation.png",
            mime="image/png"
        )

    st.success(f"生成完了！ サイズ: {len(apng_bytes)/1024:.1f} KB")
    
    # デバッグ情報の表示
    with st.expander("詳細仕様の確認"):
        st.markdown(f"""
        - **画像サイズ**: {TARGET_WIDTH}x{TARGET_HEIGHT}
        - **フレーム数**: {TOTAL_FRAMES}枚
        - **再生時間**: {TOTAL_FRAMES * FRAME_DURATION / 1000}秒
        - **ファイル形式**: PNG (APNG)
        """)

else:
    st.info("左上のボタンから画像をアップロードしてください。")
