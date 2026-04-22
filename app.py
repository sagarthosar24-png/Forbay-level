import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(layout="wide", page_title="Hydro Shift Tool")
st.title("⚓ Manual Anchor-Point Level Tool")

st.sidebar.header("Step 1: Calibration")
# We use 94.5 as the primary anchor because it's clearly marked 'FRL'
anchor_rl = 94.500 

# This defines how many pixels represent 1 meter at this specific camera angle
pixels_per_meter = st.sidebar.slider("Scale: Pixels per 1.0m", 50, 800, 300)

uploaded_file = st.file_uploader("Upload Gauge Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    h, w, _ = img_array.shape

    st.subheader("Step 2: Align the Lines")
    col_img, col_res = st.columns([3, 1])

    with st.sidebar:
        st.header("Step 3: Fine Adjust")
        # Move the anchor to exactly where 94.5 is in THIS specific photo
        anchor_y = st.slider("Move YELLOW line to 94.50m Mark", 0, h, int(h/3))
        # Move the water line to the surface
        water_y = st.slider("Move RED line to Water Surface", 0, h, int(h/2))

    # --- THE MATH ---
    # Difference in pixels (positive if water is below anchor)
    pixel_diff = water_y - anchor_y
    # Convert pixels to meters
    meter_diff = pixel_diff / pixels_per_meter
    # Final RL = Anchor - Difference (since higher Y pixel means lower elevation)
    calculated_rl = anchor_rl - meter_diff

    # --- DRAWING ---
    output_img = img_array.copy()
    
    # Draw Anchor Line (Yellow)
    cv2.line(output_img, (0, anchor_y), (w, anchor_y), (255, 255, 0), 4)
    cv2.putText(output_img, "94.50m (FRL) ANCHOR", (20, anchor_y - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

    # Draw Water Line (Red)
    cv2.line(output_img, (0, water_y), (w, water_y), (255, 0, 0), 8)
    cv2.putText(output_img, f"WATER LEVEL: {calculated_rl:.3f}m", (20, water_y + 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)

    with col_img:
        st.image(output_img, use_container_width=True)
    
    with col_res:
        st.metric("Final RL", f"{calculated_rl:.3f} m")
        st.info(f"Water is {meter_diff:.3f}m below FRL")
        
        # Display storage calculation if you have your MCM table ready
        # st.write(f"Estimated Storage: {calculate_mcm(calculated_rl)} MCM")
