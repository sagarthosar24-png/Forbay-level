import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("📏 Precise 3-Point Calibration Tool")

# --- 1. SIDEBAR: MATCH THESE TO THE PAINTED LINES ---
st.sidebar.header("Calibration (3 Points)")
y95 = st.sidebar.number_input("Pixel Y for 95.00m mark", value=206)
y94_5 = st.sidebar.number_input("Pixel Y for 94.50m mark", value=325)
y94 = st.sidebar.number_input("Pixel Y for 94.00m mark", value=453)

uploaded_file = st.file_uploader("Upload Gauge Photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    h, w, _ = img_array.shape

    # Slider for the actual water surface
    water_y = st.slider("Move Red Line to Water Surface", 0, h, y94)

    # --- 2. THE NON-LINEAR MATH ---
    # We create a mapping: [Pixels] -> [RL]
    # This handles the camera angle distortion
    pixels = np.array([y95, y94_5, y94])
    levels = np.array([95.00, 94.50, 94.00])
    
    # Fit a polynomial (Degree 2) to account for the camera tilt
    z = np.polyfit(pixels, levels, 2)
    p = np.poly1d(z)
    
    calculated_rl = p(water_y)

    # --- 3. VISUAL FEEDBACK ---
    output_img = img_array.copy()
    # Red Pointer
    cv2.line(output_img, (0, water_y), (w, water_y), (255, 0, 0), 8)
    # Green Reference Marks
    for py, lbl in zip([y95, y94_5, y94], ["95", "94.5", "94"]):
        cv2.line(output_img, (0, py), (100, py), (0, 255, 0), 4)
        cv2.putText(output_img, lbl, (110, py), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    st.image(output_img, use_container_width=True)
    st.metric("Calculated Level", f"{calculated_rl:.3f} m")
