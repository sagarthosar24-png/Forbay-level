import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Hydro Level Tool", layout="wide")
st.title("📏 Precise Gauge Calculator (90m - 95m)")

# --- 1. SIDEBAR CALIBRATION ---
st.sidebar.header("Calibration")
# Based on your input: Range is 90 to 95
max_rl = 95.000
min_rl = 90.000

# You adjust these two to match the physical lines in your photo
y_95_pixel = st.sidebar.number_input("Pixel Y for 95.00m", value=100)
y_94_pixel = st.sidebar.number_input("Pixel Y for 94.00m", value=300)

# Calculate pixels per meter based on the 1m gap between 95 and 94
pixels_per_meter = y_94_pixel - y_95_pixel

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    h, w, _ = img_array.shape

    # --- 2. DUAL-SLIDER ADJUSTMENT ---
    st.subheader("Adjust Pointer to Water Line")
    
    # Coarse slider for big movements
    coarse_y = st.slider("Coarse Adjustment", 0, h, int(h/2))
    # Fine slider for pixel-perfect alignment
    fine_y = st.slider("Fine Tuning (+/- 20 pixels)", -20, 20, 0)
    
    final_water_y = coarse_y + fine_y

    # --- 3. THE MATH ---
    # Since 94.00 is our closest reference:
    # RL = 94.00 + (Distance from 94 / Pixels per meter)
    # Note: If water is BELOW 94, distance from 94 will be negative, giving 93.xx
    dist_from_94_px = y_94_pixel - final_water_y
    calculated_rl = 94.00 + (dist_from_94_px / pixels_per_meter)

    # --- 4. DISPLAY ---
    output_img = img_array.copy()
    # Red Line (Pointer)
    cv2.line(output_img, (0, final_water_y), (w, final_water_y), (255, 0, 0), 6)
    # Green Reference Lines
    cv2.line(output_img, (0, y_95_pixel), (int(w/6), y_95_pixel), (0, 255, 0), 4)
    cv2.line(output_img, (0, y_94_pixel), (int(w/6), y_94_pixel), (0, 255, 0), 4)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.image(output_img, use_container_width=True)
    with col2:
        st.metric("Calculated Level", f"{calculated_rl:.3f} m")
        st.write(f"**Reference 95 RL:** {y_95_pixel}px")
        st.write(f"**Reference 94 RL:** {y_94_pixel}px")
        
        if calculated_rl < 91.00:
            st.error("Low Level Warning")
