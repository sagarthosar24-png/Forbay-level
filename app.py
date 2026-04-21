import streamlit as st
import cv2
import numpy as np
from PIL import Image

# --- CALIBRATION (Adjust these for the new camera angle) ---
# Open your photo in Paint to find these Y-coordinates
GAUGE_TOP_RL = 95.00
GAUGE_BOTTOM_RL = 94.00
PIXEL_Y_AT_95 = 50   # Example: Y-coordinate of 95.0 mark
PIXEL_Y_AT_94 = 450  # Example: Y-coordinate of 94.0 mark

st.set_page_config(page_title="Hydro Plant Level Detector", layout="wide")
st.title("🌊 Night-Vision Water Level Reader")

uploaded_file = st.file_uploader("Upload Night Gauge Photo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    h, w, _ = img.shape

    # --- STEP 1: CROP TO GAUGE (ROI) ---
    # We focus on the middle-top where the gauge window is
    # Adjust these percentages if the gauge moves in the frame
    roi_x1, roi_x2 = int(w * 0.4), int(w * 0.65)
    roi_y1, roi_y2 = int(h * 0.05), int(h * 0.6)
    roi = img[roi_y1:roi_y2, roi_x1:roi_x2]

    # --- STEP 2: ENHANCE DARK AREAS ---
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # CLAHE spreads out the contrast in dark images
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray_roi)

    # --- STEP 3: FIND THE WATER LINE ---
    # We look for the sharpest horizontal change in brightness
    edges = cv2.Sobel(enhanced, cv2.CV_64F, 0, 1, ksize=5)
    edges = np.absolute(edges)
    edges = np.uint8(255 * edges / np.max(edges))
    
    # Find the row with the most 'edge' activity
    row_sums = np.sum(edges, axis=1)
    relative_water_y = np.argmax(row_sums)
    absolute_water_y = relative_water_y + roi_y1

    # --- STEP 4: CALCULATION ---
    pixel_range = PIXEL_Y_AT_94 - PIXEL_Y_AT_95
    level_diff = PIXEL_Y_AT_94 - absolute_water_y
    calculated_rl = GAUGE_BOTTOM_RL + (level_diff / pixel_range)

    # --- DISPLAY ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Analysis Area (Enhanced)")
        # Draw a line on the enhanced ROI for feedback
        cv2.line(enhanced, (0, relative_water_y), (roi.shape[1], relative_water_y), 255, 3)
        st.image(enhanced, use_container_width=True)

    with col2:
        st.subheader("Final Result")
        st.metric("Calculated RL", f"{calculated_rl:.3f} m")
        
        # Draw on original image for the user
        output_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.line(output_img, (roi_x1, absolute_water_y), (roi_x2, absolute_water_y), (255, 0, 0), 10)
        st.image(output_img, use_container_width=True)
