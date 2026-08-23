import streamlit as st
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import os
import streamlit.components.v1 as components
from streamlit_js_eval import get_geolocation

from utils.gps_extract import extract_gps
from utils.map_view import generate_map
from database.db import init_db, log_detection, get_all_detections

init_db()
model = YOLO('model/potholevision_best.onnx')

st.title("PotholeVision")

mode = st.radio("Choose input type:", ["Image Upload", "Webcam (Live)"])

# ---------------- IMAGE UPLOAD MODE ----------------
if mode == "Image Upload":
    st.write("Upload a road image to detect potholes.")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        uploaded_file.seek(0)
        lat, lon = extract_gps(uploaded_file)
        uploaded_file.seek(0)

        image = Image.open(uploaded_file)
        st.subheader("Original Image")
        st.image(image, use_container_width=True)

        results = model(image)
        result_image = results[0].plot()

        st.subheader("Detection Result")
        st.image(result_image, channels="BGR", use_container_width=True)

        num_detections = len(results[0].boxes)
        st.write(f"**Potholes detected: {num_detections}**")

        if lat is not None:
            st.write(f"📍 GPS location found: {lat:.6f}, {lon:.6f}")
        else:
            st.write("📍 No GPS data found in this image.")

        if num_detections > 0:
            for box in results[0].boxes:
                confidence = float(box.conf[0])
                log_detection(lat, lon, confidence, uploaded_file.name)
            st.success(f"Logged {num_detections} detection(s) to database.")

# ---------------- WEBCAM (LIVE) MODE ----------------
elif mode == "Webcam (Live)":
    st.write("Live webcam pothole detection. Click 'Start' below.")

    location = get_geolocation()
    if location:
        webcam_lat = location['coords']['latitude']
        webcam_lon = location['coords']['longitude']
        st.write(f"📍 Using browser location: {webcam_lat:.6f}, {webcam_lon:.6f}")
    else:
        webcam_lat, webcam_lon = None, None
        st.write("📍 Location not available (permission denied or unsupported).")

    run = st.checkbox("Start webcam")
    frame_placeholder = st.empty()
    detection_count_placeholder = st.empty()

    if run:
        cap = cv2.VideoCapture(0)
        frame_count = 0
        detect_every_n_frames = 3
        last_results = None

        while run:
            ret, frame = cap.read()
            if not ret:
                st.error("Could not access webcam.")
                break

            frame_count += 1

            if frame_count % detect_every_n_frames == 0 or last_results is None:
                results = model(frame, verbose=False)
                last_results = results

                if webcam_lat is not None and len(results[0].boxes) > 0:
                    for box in results[0].boxes:
                        confidence = float(box.conf[0])
                        log_detection(webcam_lat, webcam_lon, confidence, "webcam_frame")

            annotated_frame = last_results[0].plot()
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(annotated_frame_rgb, use_container_width=True)

            num_detections = len(last_results[0].boxes)
            detection_count_placeholder.write(f"**Potholes detected in frame: {num_detections}**")

            run = st.session_state.get("Start webcam", run)

        cap.release()

# ---------------- MAP GENERATION (always available) ----------------
st.divider()
if st.button("🗺️ Generate Pothole Map"):
    all_detections = get_all_detections()
    geo_detections = [d for d in all_detections if d[2] is not None]
    map_path = generate_map(geo_detections)
    if map_path:
        st.success("Map generated below:")
        with open(map_path, 'r', encoding='utf-8') as f:
            map_html = f.read()
        components.html(map_html, height=500)
    else:
        st.info("No GPS-tagged detections yet.") 