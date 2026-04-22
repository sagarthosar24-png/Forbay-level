import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("⚓ Precision Anchor Level Tool")

# --- 1. SIDEBAR CONFIGURATION ---
st.sidebar.header("Step 1: Calibration")
# Adjust how many pixels = 1 meter based on the gap between 95 and 94.5
px_per_05m = st.sidebar.number_input("Pixels between 95.0 and 94.5", value=150)
pixels_per_meter = px_per_05m * 2

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    h, w, _ = img_array.shape

    # --- 2. THE PRECISION CONTROLS ---
    st.subheader("Step 2: Position the Lines (Use +/- for Precision)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # Number input allows single-pixel adjustment
        anchor_y = st.number_input("YELLOW Anchor (Set to 94.50m Mark)", 0, h, int(h/3))
        st.slider("Slide for Anchor", 0, h, anchor_y, key="anchor_slider", label_visibility="collapsed")
        
    with col_b:
        water_y = st.number_input("RED Pointer (Set to Water Surface)", 0, h, int(h/2))
        st.slider("Slide for Water", 0, h, water_y, key="water_slider", label_visibility="collapsed")

    # --- 3. THE CALCULATION ---
    pixel_diff = water_y - anchor_y
    meter_diff = pixel_diff / pixels_per_meter
    calculated_rl = 94.500 - meter_diff

    # --- 4. DRAWING ---
    output_img = img_array.copy()
    
    # Draw Anchor (Yellow)
    cv2.line(output_img, (0, int(anchor_y)), (w, int(anchor_y)), (255, 255, 0), 3)
    cv2.putText(output_img, "94.50m Anchor", (20, int(anchor_y) - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # Draw Water (Red)
    cv2.line(output_img, (0, int(water_y)), (w, int(water_y)), (255, 0, 0), 6)

    # --- 5. OUTPUT ---
    main_col, res_col = st.columns([4, 1])
    with main_col:
        st.image(output_img, use_container_width=True)
    with res_col:
        st.metric("Level (RL)", f"{calculated_rl:.3f} m")
        if calculated_rl < 93.50:
            st.warning(f"Calculated: {calculated_rl:.3f}m")
