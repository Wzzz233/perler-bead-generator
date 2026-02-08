import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas
import io

st.set_page_config(page_title="拼豆生成器", page_icon="🧶", layout="wide")
st.title("🧶 拼豆 (Perler Bead) 设计图生成器")

# 将设置从侧边栏移到主界面，方便手机操作
st.caption("👈 点击左上角箭头可展开更多高级设置 (如网格大小)")

# 主要模式选择直接放在顶部
mode = st.radio("🎨 选择模式", ["上传图片生成", "自己画图"], horizontal=True)

# 高级设置保留在侧边栏，避免主界面太乱
with st.sidebar:
    st.header("⚙️ 参数设置")
    c1, c2 = st.columns(2)
    grid_w = c1.number_input("宽度 (豆)", 10, 100, 30)
    grid_h = c2.number_input("高度 (豆)", 10, 100, 30)
    n_colors = st.slider("限制颜色数量", 2, 64, 16)
    show_grid = st.checkbox("显示网格线", True)

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

if mode == "上传图片生成":
    up = st.file_uploader("点击上传图片", type=["png", "jpg", "jpeg"])
    if up: src = Image.open(up)

elif mode == "自己画图":
    col_tools, col_canvas = st.columns([1, 3])
    
    with col_tools:
        st.write("🖌️ 画笔设置")
        stroke_color = st.color_picker("画笔颜色", "#000000")
        stroke_width = st.slider("画笔粗细", 1, 50, 10)
        bg_color = st.color_picker("背景颜色", "#ffffff")
        
    with col_canvas:
        # 实时更新的画板
        canvas = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # 固定填充色（目前用不到）
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            update_streamlit=True,
            height=400,
            width=400,
            drawing_mode="freedraw",
            key="canvas",
        )
        
    # 获取画板内容
    if canvas.image_data is not None:
        # 转换为 RGB 图像
        src = Image.fromarray(canvas.image_data.astype("uint8")).convert("RGB")

# 生成结果展示
if src:
    st.divider()
    st.subheader("🎨 生成结果")
    
    # 手机上单列显示更好看
    st.image(src, "原始输入预览", width=200)
    
    p_data, disp, sc = pixelate(src, grid_w, grid_h, n_colors)
    if show_grid: disp = add_grid(disp, grid_w, grid_h, sc)
    
    st.image(disp, caption=f"拼豆设计图 ({grid_w}x{grid_h})", use_column_width=True)
    
    # 下载按钮
    buf = io.BytesIO()
    disp.save(buf, format="PNG")
    st.download_button("📥 下载设计图纸", buf.getvalue(), "pattern.png", "image/png", use_container_width=True)
    
    # 统计区域
    st.subheader("📊 颜色统计")
    cnt = {}
    for c in list(p_data.getdata()):
        h = '#{:02x}{:02x}{:02x}'.format(*c)
        cnt[h] = cnt.get(h, 0) + 1
    
    cols = st.columns(6)
    for i, (col, n) in enumerate(sorted(cnt.items(), key=lambda x:x[1], reverse=True)):
        # 过滤掉纯白色背景（如果是背景色的话）
        if col.lower() == bg_color.lower() and mode == "自己画图":
            continue
            
        with cols[i%6]:
            st.markdown(f'<div style="background-color:{col};width:100%;height:30px;border-radius:5px;border:1px solid #ccc;"></div>', unsafe_allow_html=True)
            st.caption(f"{n}颗")
