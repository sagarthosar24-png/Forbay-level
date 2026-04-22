import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("⚓ Anchor-Point Level Calculator")

# --- 1. SET THE SCALE ---
st.sidebar.header("1. Scale Calibration")
st.sidebar.info("First, find the distance between two known marks on your gauge.")
y_95 = st.sidebar.number_input("Pixel Y for 95.00m", value=200)
y_94_5 = st.sidebar.number_input("Pixel Y for 94.50m (FRL)", value=320)

# Calculate how many pixels represent 0.5 meters
pixels_per_half_meter = y_94_5 - y_95
pixels_per_meter = pixels_per_half_meter * 2

uploaded_file = st.file_uploader("Upload Gauge Photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    h, w, _ = img_array.shape

    # --- 2. ADJUST THE WATER POINTER ---
    st.subheader("2. Match the Red Line to the Water Surface")
    water_y = st.slider("Water Surface Pointer", 0, h, y_94_5 + 100)

    # --- 3. THE CALCULATION ---
    # We calculate distance relative to the 94.5m anchor
    pixel_diff = y_94_5 - water_y
    # Convert pixels to meters
    meter_diff = pixel_diff / pixels_per_meter
    # Final RL = 94.5 + (difference)
    calculated_rl = 94.500 + meter_diff

    # --- 4. DRAWING ---
    output_img = img_array.copy()
    
    # Yellow Anchor Line (Fixed at 94.5)
    cv2.line(output_img, (0, y_94_5), (w, y_94_5), (255, 255, 0), 3)
    cv2.putText(output_img, "ANCHOR: 94.50m", (10, y_94_5 - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    # Red Water Line (Moveable)
    cv2.line(output_img, (0, water_y), (w, water_y), (255, 0, 0), 8)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.image(output_img, use_container_width=True)
    with col2:
        st.metric("Final Water Level", f"{calculated_rl:.3f} m")
        st.write(f"**Distance from FRL:** {abs(meter_diff):.3f} meters")
        
        if calculated_rl < 93.50:
            st.warning("Level is below 93.50m")
