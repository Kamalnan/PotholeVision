import streamlit as st
from ultralytics import YOLO
from PIL import Image
import folium
from streamlit_folium import st_folium
import cv2
import numpy as np

from utils.gps_extract import extract_gps
from database.db import init_db, log_detection, get_all_detections

init_db()
model = YOLO('model/potholevision_best.pt')

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
    run = st.checkbox("Start webcam")
    frame_placeholder = st.empty()
    detection_count_placeholder = st.empty()

    if run:
        cap = cv2.VideoCapture(0)  # 0 = default webcam
        while run:
            ret, frame = cap.read()
            if not ret:
                st.error("Could not access webcam.")
                break

            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()

            # Convert BGR (OpenCV) to RGB (Streamlit expects RGB for st.image by default here)
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(annotated_frame_rgb, use_container_width=True)

            num_detections = len(results[0].boxes)
            detection_count_placeholder.write(f"**Potholes detected in frame: {num_detections}**")

            # Re-check the checkbox state each loop so "Stop" actually works
            run = st.session_state.get("Start webcam", run)

        cap.release()

# ---------------- MAP SECTION (always shown) ----------------
st.subheader("Pothole Map")
all_detections = get_all_detections()
geo_detections = [d for d in all_detections if d[2] is not None]

if geo_detections:
    avg_lat = sum(d[2] for d in geo_detections) / len(geo_detections)
    avg_lon = sum(d[3] for d in geo_detections) / len(geo_detections)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15)

    for d in geo_detections:
        _, timestamp, lat_, lon_, conf, path, times = d
        folium.Marker(
            location=[lat_, lon_],
            popup=f"Confidence: {conf:.2f}<br>Seen {times}x<br>Last: {timestamp}",
            icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
        ).add_to(m)

    st_folium(m, width=700, height=450)
else:
    st.info("No GPS-tagged detections logged yet.")