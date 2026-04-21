import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("Water Level Detector")

uploaded_file = st.file_uploader("Upload Gauge Photo", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    # Convert uploaded file to OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    # Run your detection logic here
    # level_pixel = detect_water_level(img) 
    
    st.image(img, caption='Processed Image', use_column_width=True)
    st.success(f"Detected Water Level: {calculated_rl} m")
