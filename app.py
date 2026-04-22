import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("⚓ Synchronized Precision Gauge Tool")

# --- 1. SETUP SESSION STATE ---
# This ensures the sliders and boxes stay 'synced' and actually shift the lines
if 'anchor_y' not in st.session_state:
    st.session_state.anchor_y = 300
if 'water_y' not in st.session_state:
    st.session_state.water_y = 500

# --- 2. SIDEBAR CALIBRATION ---
st.sidebar.header("Step 1: Scale Calibration")
px_per_05m = st.sidebar.number_input("Pixels per 0.5m (95.0 to 94.5)", value=150)
pixels_per_meter = px_per_05m * 2

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    h, w, _ = img_array.shape

    # --- 3. PRECISION CONTROLS (SYNCED) ---
    st.subheader("Step 2: Position the Lines")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**YELLOW Anchor (94.50m)**")
        # Number box updates the session state
        st.number_input("Pixel Position", 0, h, key="anchor_y")
        # Slider also updates the same session state
        st.slider("Slide to 94.5 mark", 0, h, key="anchor_y", label_visibility="collapsed")
        
    with col_b:
        st.markdown("**RED Water Line**")
        st.number_input("Pixel Position", 0, h, key="water_y")
        st.slider("Slide to water surface", 0, h, key="water_y", label_visibility="collapsed")

    # --- 4. CALCULATION ---
    # Using the session state values directly
    pixel_diff = st.session_state.water_y - st.session_state.anchor_y
    meter_diff = pixel_diff / pixels_per_meter
    calculated_rl = 94.500 - meter_diff

    # --- 5. DRAWING ---
    output_img = img_array.copy()
    
    # Draw Anchor (Yellow)
    ay = int(st.session_state.anchor_y)
    cv2.line(output_img, (0, ay), (w, ay), (255, 255, 0), 4)
    cv2.putText(output_img, "94.50m FRL", (20, ay - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

    # Draw Water (Red)
    wy = int(st.session_state.water_y)
    cv2.line(output_img, (0, wy), (w, wy), (255, 0, 0), 8)

    # --- 6. DISPLAY ---
    main_col, res_col = st.columns([3, 1])
    with main_col:
        st.image(output_img, use_container_width=True)
    with res_col:
        st.metric("Detected RL", f"{calculated_rl:.3f} m")
        st.info(f"Anchor Y: {ay}")
        st.info(f"Water Y: {wy}")
