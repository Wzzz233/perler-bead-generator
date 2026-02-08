import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas
import io

st.set_page_config(page_title="拼豆生成器", page_icon="🧶", layout="wide")
st.title("🧶 拼豆 (Perler Bead) 设计图生成器")

with st.sidebar:
    st.header("设置")
    mode = st.radio("模式", ["上传图片", "手动绘制"])
    c1, c2 = st.columns(2)
    grid_w = c1.number_input("宽 (豆)", 10, 100, 30)
    grid_h = c2.number_input("高 (豆)", 10, 100, 30)
    n_colors = st.slider("颜色数量", 2, 64, 16)
    show_grid = st.checkbox("显示网格", True)

def pixelate(img, w, h, colors):
    img = img.resize((w, h), Image.Resampling.NEAREST)
    res = img.quantize(colors=colors).convert('RGB')
    scale = 20
    large = res.resize((w*scale, h*scale), Image.Resampling.NEAREST)
    return res, large, scale

def add_grid(img, w, h, scale):
    draw = ImageDraw.Draw(img)
    for x in range(0, w*scale, scale):
        draw.line([(x, 0), (x, h*scale)], fill=(200,200,200), width=1)
    for y in range(0, h*scale, scale):
        draw.line([(0, y), (w*scale, y)], fill=(200,200,200), width=1)
    return img

src = None
if mode == "上传图片":
    up = st.file_uploader("选择图片", type=["png", "jpg", "jpeg"])
    if up: src = Image.open(up)
else:
    st.info("左键绘图，右键擦除")
    canvas = st_canvas(fill_color="#fff", stroke_width=10, stroke_color="#000", background_color="#fff", height=400, width=400, drawing_mode="freedraw", key="canvas")
    if canvas.image_data is not None:
        src = Image.fromarray(canvas.image_data.astype("uint8"), "RGBA").convert("RGB")

if src:
    st.divider()
    c1, c2 = st.columns([1, 2])
    c1.image(src, "原始输入", use_column_width=True)
    
    p_data, disp, sc = pixelate(src, grid_w, grid_h, n_colors)
    if show_grid: disp = add_grid(disp, grid_w, grid_h, sc)
    
    with c2:
        st.image(disp, f"设计图 ({grid_w}x{grid_h})")
        buf = io.BytesIO()
        disp.save(buf, format="PNG")
        st.download_button("下载图纸", buf.getvalue(), "pattern.png", "image/png")
    
    st.subheader("用量统计")
    cnt = {}
    for c in list(p_data.getdata()):
        h = '#{:02x}{:02x}{:02x}'.format(*c)
        cnt[h] = cnt.get(h, 0) + 1
    
    cols = st.columns(8)
    for i, (col, n) in enumerate(sorted(cnt.items(), key=lambda x:x[1], reverse=True)):
        cols[i%8].markdown(f'<div style="background-color:{col};width:30px;height:30px;border-radius:50%;border:1px solid #ccc;"></div>{n}', unsafe_allow_html=True)
