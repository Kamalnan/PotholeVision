import streamlit as st
from ultralytics import YOLO
from PIL import Image

# Load our trained pothole model once, when the app starts
model = YOLO('model/potholevision_best.pt')

st.title("PotholeVision")
st.write("Upload a road image to detect potholes.")

# File uploader widget
uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Open the uploaded image
    image = Image.open(uploaded_file)

    # Show the original image
    st.subheader("Original Image")
    st.image(image, use_container_width=True)

    # Run detection
    results = model(image)

    # Get the image with boxes drawn (as a numpy array), then display it
    result_image = results[0].plot()
    st.subheader("Detection Result")
    st.image(result_image, channels="BGR", use_container_width=True)

    # Show how many potholes were found
    num_detections = len(results[0].boxes)
    st.write(f"**Potholes detected: {num_detections}**")