from ultralytics import YOLO

# Load OUR trained pothole model (not the generic pretrained one)
model = YOLO('model/potholevision_best.pt')

# Run detection on a test image from our validation set
results = model('data/pothole-dataset/valid/images', save=True)

print("Detection complete. Check the 'runs/detect/predict' folder for results.")