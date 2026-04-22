import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(layout="wide", page_title="Hydro Shift Tool")
st.title("⚓ Precision Anchor Gauge Tool")

# --- 1. SYNC FUNCTIONS ---
def update_slider_a():
    st.session_state.slider_a = st.session_state.num_a
def update_num_a():
    st.session_state.num_a = st.session_state.slider_a

def update_slider_w():
    st.session_state.slider_w = st.session_state.num_w
def update_num_w():
    st.session_state.num_w = st.session_state.slider_w

# --- 2. SIDEBAR CALIBRATION ---
st.sidebar.header("Step 1: Scale Calibration")
px_per_05m = st.sidebar.number_input("Pixels per 0.5m (95.0 to 94.5)", value=150)
pixels_per_meter = px_per_05m * 2

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    h, w, _ = img_array.shape

    # Initialize session states if they don't exist
    if 'num_a' not in st.session_state:
        st.session_state.num_a = int(h/3)
    if 'slider_a' not in st.session_state:
        st.session_state.slider_a = int(h/3)
    if 'num_w' not in st.session_state:
        st.session_state.num_w = int(h/2)
    if 'slider_w' not in st.session_state:
        st.session_state.slider_w = int(h/2)

    # --- 3. PRECISION CONTROLS ---
    st.subheader("Step 2: Position the Lines")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**YELLOW Anchor (94.50m)**")
        ay = st.number_input("Pixel Position", 0, h, key="num_a", on_change=update_slider_a)
        st.slider("Slide Anchor", 0, h, key="slider_a", on_change=update_num_a, label_visibility="collapsed")
        
    with col_b:
        st.markdown("**RED Water Line**")
        wy = st.number_input("Pixel Position ", 0, h, key="num_w", on_change=update_slider_w)
        st.slider("Slide Water", 0, h, key="slider_w", on_change=update_num_w, label_visibility="collapsed")

    # --- 4. CALCULATION ---
    pixel_diff = wy - ay
    meter_diff = pixel_diff / pixels_per_meter
    calculated_rl = 94.500 - meter_diff

    # --- 5. DRAWING ---
    output_img = img_array.copy()
    cv2.line(output_img, (0, int(ay)), (w, int(ay)), (255, 255, 0), 4) # Anchor
    cv2.putText(output_img, "94.50m FRL", (20, int(ay) - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
    
    cv2.line(output_img, (0, int(wy)), (w, int(wy)), (255, 0, 0), 8) # Water

    # --- 6. DISPLAY ---
    main_col, res_col = st.columns([3, 1])
    with main_col:
        st.image(output_img, use_container_width=True)
    with res_col:
        st.metric("Detected RL", f"{calculated_rl:.3f} m")
        st.info(f"Anchor Y: {int(ay)}")
        st.info(f"Water Y: {int(wy)}")
