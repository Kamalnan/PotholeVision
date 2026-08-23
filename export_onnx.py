from ultralytics import YOLO

model = YOLO('model/potholevision_best.pt')
model.export(format='onnx', imgsz=416)