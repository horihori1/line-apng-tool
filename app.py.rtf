{\rtf1\ansi\ansicpg932\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
from PIL import Image, ImageDraw, ImageOps\
import io\
\
# ==========================================\
# LINE\uc0\u24195 \u21578  (Small Image) \u21427 \u26684 \u20181 \u27096 \u35373 \u23450 \
# ==========================================\
TARGET_WIDTH = 600\
TARGET_HEIGHT = 400\
TOTAL_FRAMES = 10  # \uc0\u35201 \u20214 \u12300 5\u65374 20\u26522 \u12301 \u12434 \u28288 \u12383 \u12377 \u12383 \u12417 10\u26522 \u12391 \u22266 \u23450 \
MAX_KB_SIZE = 300  # \uc0\u35201 \u20214 \u12300 300KB\u20197 \u19979 \u12301 \
\
def create_checkmark_icon(size):\
    """\uc0\u32209 \u12398 \u20870 \u65291 \u30333 \u12356 \u12481 \u12455 \u12483 \u12463 \u12510 \u12540 \u12463 \u12434 \u25551 \u30011 """\
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))\
    draw = ImageDraw.Draw(img)\
    \
    # \uc0\u39854 \u12420 \u12363 \u12394 \u32209  (#00C853)\
    padding = size * 0.05\
    draw.ellipse([padding, padding, size - padding, size - padding], fill="#00C853", outline=None)\
    \
    # \uc0\u12481 \u12455 \u12483 \u12463 \u12510 \u12540 \u12463 \
    points = [(size * 0.28, size * 0.52), (size * 0.45, size * 0.70), (size * 0.75, size * 0.35)]\
    stroke_width = int(size * 0.12)\
    draw.line(points, fill="white", width=stroke_width, joint="curve")\
    return img\
\
def create_strict_line_apng(base_image, total_duration_sec, loop_count):\
    """\
    LINE\uc0\u24195 \u21578 \u12398 \u20181 \u27096 \u12434 \u24375 \u21046 \u30340 \u12395 \u23432 \u12387 \u12383 APNG\u12434 \u20316 \u25104 \u12377 \u12427 \
    """\
    # 1. \uc0\u30011 \u20687 \u12398 \u12522 \u12469 \u12452 \u12474  (600x400)\
    # ImageOps.fit \uc0\u12434 \u20351 \u12356 \u12289 \u30011 \u20687 \u12398 \u20013 \u24515 \u12434 \u12488 \u12522 \u12511 \u12531 \u12464 \u12375 \u12390 \u38553 \u38291 \u12394 \u12367 \u22475 \u12417 \u12427 \
    base_img = base_image.convert("RGBA")\
    base_img = ImageOps.fit(base_img, (TARGET_WIDTH, TARGET_HEIGHT), method=Image.Resampling.LANCZOS)\
\
    # 2. \uc0\u12450 \u12452 \u12467 \u12531 \u20316 \u25104 \
    icon_size = int(TARGET_HEIGHT * 0.25) # \uc0\u39640 \u12373 \u12398 25% (\u32004 100px)\
    checkmark_icon = create_checkmark_icon(icon_size)\
    margin = 20\
\
    positions = [\
        (margin, margin),                                      # \uc0\u24038 \u19978 \
        (TARGET_WIDTH - icon_size - margin, margin),           # \uc0\u21491 \u19978 \
        (margin, TARGET_HEIGHT - icon_size - margin),          # \uc0\u24038 \u19979 \
        (TARGET_WIDTH - icon_size - margin, TARGET_HEIGHT - icon_size - margin) # \uc0\u21491 \u19979 \
    ]\
\
    # 3. \uc0\u12501 \u12524 \u12540 \u12512 \u29983 \u25104  (\u35201 \u20214 : 5\u65374 20\u12501 \u12524 \u12540 \u12512 )\
    # \uc0\u12371 \u12371 \u12391 \u12399 \u12300 10\u12501 \u12524 \u12540 \u12512 \u12301 \u20316 \u25104 \u12375 \u12414 \u12377 \u12290 \
    # \uc0\u21069 \u21322 5\u12501 \u12524 \u12540 \u12512 : \u12481 \u12455 \u12483 \u12463 \u12354 \u12426  / \u24460 \u21322 5\u12501 \u12524 \u12540 \u12512 : \u12481 \u12455 \u12483 \u12463 \u12394 \u12375 \
    \
    frame_on = base_img.copy()\
    for pos in positions:\
        frame_on.paste(checkmark_icon, pos, checkmark_icon)\
    \
    frame_off = base_img.copy()\
\
    frames = []\
    # ON\uc0\u12434 5\u26522 \u36861 \u21152 \
    for _ in range(5):\
        frames.append(frame_on)\
    # OFF\uc0\u12434 5\u26522 \u36861 \u21152 \
    for _ in range(5):\
        frames.append(frame_off)\
\
    # 4. 1\uc0\u12501 \u12524 \u12540 \u12512 \u12354 \u12383 \u12426 \u12398 \u34920 \u31034 \u26178 \u38291 \u12434 \u35336 \u31639 \
    # \uc0\u25351 \u23450 \u31186 \u25968 (ms) \'f7 \u12501 \u12524 \u12540 \u12512 \u25968 (10)\
    duration_per_frame = int((total_duration_sec * 1000) / TOTAL_FRAMES)\
\
    # 5. \uc0\u20445 \u23384  (\u23481 \u37327 \u21066 \u28187 \u20966 \u29702 \u20184 \u12365 )\
    output_io = io.BytesIO()\
    \
    # \uc0\u33394 \u25968 \u12434 \u28187 \u12425 \u12375 \u12390 300KB\u20197 \u19979 \u12434 \u30906 \u23455 \u12395 \u12377 \u12427  (Quantize)\
    # APNG\uc0\u12399 \u23481 \u37327 \u12364 \u33192 \u12425 \u12415 \u12420 \u12377 \u12356 \u12383 \u12417 \u12289 \u30011 \u36074 \u12434 \u23569 \u12375 \u35519 \u25972 \u12375 \u12390 \u23481 \u37327 \u20778 \u20808 \u12395 \u12377 \u12427 \
    frames_quantized = [f.quantize(colors=128, method=2) for f in frames]\
\
    frames_quantized[0].save(\
        output_io,\
        format="PNG",\
        save_all=True,\
        append_images=frames_quantized[1:],\
        duration=duration_per_frame,\
        loop=loop_count, # \uc0\u25351 \u23450 \u12373 \u12428 \u12383 \u12523 \u12540 \u12503 \u25968  (LINE\u12399 1~4)\
        optimize=True,\
        disposal=1\
    )\
    \
    return output_io.getvalue()\
\
# ==========================================\
# UI\uc0\u37096 \u20998 \
# ==========================================\
st.set_page_config(page_title="LINE\uc0\u24195 \u21578  APNG\u29983 \u25104 \u27231 ", layout="centered")\
\
st.title("LINE\uc0\u24195 \u21578 (Small) \u23436 \u20840 \u23550 \u24540 \u29256 ")\
st.markdown("""\
\uc0\u20197 \u19979 \u12398 \u21427 \u26684 \u12394 \u20181 \u27096 \u12395 \u33258 \u21205 \u36969 \u21512 \u12373 \u12379 \u12414 \u12377 \u65306 \
* \uc0\u12469 \u12452 \u12474 : **600x400px** (\u33258 \u21205 \u12488 \u12522 \u12511 \u12531 \u12464 )\
* \uc0\u12501 \u12524 \u12540 \u12512 \u25968 : **10\u26522 ** (\u20181 \u27096 :5-20\u26522 )\
* \uc0\u23481 \u37327 : **300KB\u20197 \u19979 ** (\u33258 \u21205 \u22311 \u32302 )\
""")\
\
# \uc0\u12469 \u12452 \u12489 \u12496 \u12540 \u35373 \u23450 \
st.sidebar.header("LINE\uc0\u24195 \u21578 \u35373 \u23450 ")\
\
# \uc0\u31186 \u25968 \u35373 \u23450  (1\u31186 \u65374 4\u31186 )\
duration = st.sidebar.slider("\uc0\u12450 \u12491 \u12513 \u12540 \u12471 \u12519 \u12531 \u31186 \u25968 ", 1.0, 4.0, 2.0, 0.5, help="\u20181 \u27096 : \u26368 \u30701 1\u31186 \u12289 \u26368 \u38263 4\u31186 ")\
\
# \uc0\u12523 \u12540 \u12503 \u25968 \u35373 \u23450  (1\u22238 \u65374 4\u22238 )\
loop_num = st.sidebar.slider("\uc0\u12523 \u12540 \u12503 \u22238 \u25968 ", 1, 4, 0, 1, help="\u20181 \u27096 : 1\u65374 4\u22238  (\u28961 \u38480 \u12523 \u12540 \u12503 \u19981 \u21487 )")\
\
\
uploaded_file = st.file_uploader("\uc0\u30011 \u20687 \u12434 \u12450 \u12483 \u12503 \u12525 \u12540 \u12489 ", type=["jpg", "jpeg", "png"])\
\
if uploaded_file:\
    image = Image.open(uploaded_file)\
    \
    col1, col2 = st.columns(2)\
    with col1:\
        st.subheader("\uc0\u20803 \u30011 \u20687 ")\
        st.image(image, use_container_width=True)\
\
    with col2:\
        st.subheader("\uc0\u12503 \u12524 \u12499 \u12517 \u12540 ")\
        if st.button("\uc0\u22793 \u25563 \u12539 \u29983 \u25104 \u12377 \u12427 ", type="primary"):\
            with st.spinner("\uc0\u35215 \u26684 \u12395 \u21512 \u12431 \u12379 \u12390 \u22793 \u25563 \u20013 ..."):\
                # \uc0\u29983 \u25104 \u20966 \u29702 \
                apng_data = create_strict_line_apng(image, duration, loop_num)\
                \
                # \uc0\u23481 \u37327 \u12481 \u12455 \u12483 \u12463 \
                kb_size = len(apng_data) / 1024\
                st.image(apng_data, use_container_width=True)\
                \
                st.markdown(f"**\uc0\u20181 \u19978 \u12364 \u12426 \u12469 \u12452 \u12474 : \{kb_size:.1f\}KB**")\
                \
                if kb_size <= 300:\
                    st.success("\uc0\u9989  \u23529 \u26619 \u22522 \u28310 OK (300KB\u20197 \u19979 )")\
                else:\
                    st.error("\uc0\u10060  \u23481 \u37327 \u12458 \u12540 \u12496 \u12540  (\u30011 \u20687 \u12364 \u35079 \u38609 \u12377 \u12366 \u12414 \u12377 )")\
\
                # \uc0\u12501 \u12449 \u12452 \u12523 \u21517 \u12395 \u12473 \u12506 \u12483 \u12463 \u12434 \u21547 \u12417 \u12427 \
                file_name = f"line_600x400_\{int(duration)\}s_loop\{loop_num\}.png"\
                \
                st.download_button(\
                    label="\uc0\u55357 \u56549  \u22522 \u28310 \u36969 \u21512 APNG\u12434 \u12480 \u12454 \u12531 \u12525 \u12540 \u12489 ",\
                    data=apng_data,\
                    file_name=file_name,\
                    mime="image/png"\
                )}