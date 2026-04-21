import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Manual Gauge Reader", layout="wide")
st.title("📏 Interactive Water Level Calculator")

# Sidebar for Calibration
st.sidebar.header("1. Calibration Settings")
st.sidebar.info("Set these once based on your gauge markings in the image.")
y_95 = st.sidebar.number_input("Pixel Y for 95.00 RL", value=100)
y_94 = st.sidebar.number_input("Pixel Y for 94.00 RL", value=800)

uploaded_file = st.file_uploader("Upload Gauge Photo (Day or Night)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Load Image
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    h, w, _ = img_array.shape

    st.subheader("2. Adjust Pointer to Water Line")
    
    # --- The Adjustable Pointer ---
    # This slider creates the red line you can move up and down
    water_y = st.slider("Move red line to match water surface", 0, h, int(h/2))

    # Calculate RL based on your manual adjustment
    # Formula: RL = 94 + (Pixels from 94 / Pixels per meter)
    pixels_per_meter = y_94 - y_95
    if pixels_per_meter != 0:
        dist_from_94 = y_94 - water_y
        calculated_rl = 94.00 + (dist_from_94 / pixels_per_meter)
    else:
        calculated_rl = 0.0

    # Draw the pointer on the image
    output_img = img_array.copy()
    # Draw horizontal red line
    cv2.line(output_img, (0, water_y), (w, water_y), (255, 0, 0), 8)
    
    # Optional: Draw calibration markers for visual check
    cv2.line(output_img, (0, y_95), (int(w/4), y_95), (0, 255, 0), 4) # Green line at 95
    cv2.line(output_img, (0, y_94), (int(w/4), y_94), (0, 255, 0), 4) # Green line at 94

    # Display Result
    col1, col2 = st.columns([3, 1])
    with col1:
        st.image(output_img, caption="Adjust the slider until the RED line touches the water", use_container_width=True)
    
    with col2:
        st.metric(label="Selected Water Level", value=f"{calculated_rl:.3f} RL")
        st.write(f"**Pointer Pixel:** {water_y}")
        
        if calculated_rl > 94.50:
            st.error("⚠️ HIGH LEVEL ALERT")
