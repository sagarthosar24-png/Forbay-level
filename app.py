import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Hydro Plant Level Tool", layout="wide")
st.title("📏 BTRP/Rawalje Level Calculator")

# --- STEP 1: SIDEBAR CALIBRATION ---
st.sidebar.header("1. Calibration")
st.sidebar.write("Align green lines with physical marks on the gauge.")

# Updated to your 90m minimum
max_rl = st.sidebar.number_input("Upper Mark RL (e.g. 95.0)", value=95.000, step=0.001, format="%.3f")
min_rl = st.sidebar.number_input("Lower Mark RL (e.g. 90.0)", value=90.000, step=0.001, format="%.3f")

# Pixel positions (Adjust these until the green lines match the photo marks)
y_upper_pixel = st.sidebar.number_input(f"Pixel Y for {max_rl}m", value=100)
y_lower_pixel = st.sidebar.number_input(f"Pixel Y for {min_rl}m", value=900)

uploaded_file = st.file_uploader("Upload Gauge Photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    h, w, _ = img_array.shape

    # --- STEP 2: MANUAL ADJUSTMENT ---
    st.subheader("2. Adjust Red Line to Water Level")
    water_y = st.slider("Slide to match water surface", 0, h, int(h/2))

    # --- STEP 3: CORRECTED MATH ---
    # total_rl_span is 5.0 if max is 95 and min is 90
    total_rl_span = max_rl - min_rl
    total_pixel_span = y_lower_pixel - y_upper_pixel

    if total_pixel_span != 0:
        # Calculate how many meters each pixel represents
        meters_per_pixel = total_rl_span / total_pixel_span
        
        # Distance in pixels from the lower reference (90m)
        pixel_dist_from_bottom = y_lower_pixel - water_y
        
        # Final RL calculation
        calculated_rl = min_rl + (pixel_dist_from_bottom * meters_per_pixel)
    else:
        calculated_rl = min_rl

    # --- STEP 4: DRAWING & DISPLAY ---
    output_img = img_array.copy()
    # Red pointer line
    cv2.line(output_img, (0, water_y), (w, water_y), (255, 0, 0), 10)
    
    # Green calibration markers (for 95 and 90)
    cv2.line(output_img, (0, y_upper_pixel), (int(w/5), y_upper_pixel), (0, 255, 0), 5)
    cv2.line(output_img, (0, y_lower_pixel), (int(w/5), y_lower_pixel), (0, 255, 0), 5)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.image(output_img, use_container_width=True)
    
    with col2:
        st.metric(label="Current Level", value=f"{calculated_rl:.3f} m")
        st.write(f"**Span:** {total_rl_span} meters")
        
        # Warning for your operations
        if calculated_rl >= 94.50:
            st.error("⚠️ NEAR FRL (95.00)")
        elif calculated_rl <= 90.50:
            st.warning("⚠️ NEAR MIN LEVEL (90.00)")
