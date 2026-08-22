from ultralytics import YOLO

# Load a pretrained YOLOv8 model (trained on general objects, not potholes yet)
model = YOLO('yolov8n.pt')

# Run detection on a built-in sample image (comes bundled with Ultralytics)
results = model('https://ultralytics.com/images/bus.jpg')

# Save the result image with boxes drawn, instead of trying to pop up a window
results[0].save(filename='output.jpg')
print("Saved detection result to output.jpg")