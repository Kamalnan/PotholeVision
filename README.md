# PotholeVision

A cross-platform pothole detection and monitoring system built with YOLOv8. Upload a road image or use a live webcam feed to detect potholes in real time, log each detection with GPS location (when available), and view all detected potholes on an interactive map — all from a single, self-contained application.

This is a final year engineering project, rebuilt from scratch to replace an earlier, undocumented, Linux-only implementation with a properly engineered, cross-platform, documented system.

---

## Features

- **Pothole detection** on uploaded images using a custom-trained YOLOv8 model
- **Live webcam detection**, optimized for real-time performance on CPU-only hardware
- **GPS extraction** from image EXIF metadata, when available
- **Persistent logging** of detections to a local SQLite database, with proximity-based deduplication (the same pothole seen again isn't logged as a new entry — it increments a "times detected" counter instead)
- **Interactive map view** (Folium) plotting all GPS-tagged detections
- **Fully cross-platform**: runs identically on Windows, macOS, and Linux — no OS-specific dependencies

---

## Why this project exists

The original version of this project (a typical downloaded, undocumented pothole-detection repository) worked only on Linux, had no README, no commit history beyond a single upload, and used an outdated detection approach. This rebuild addresses all of that:

| | Original | PotholeVision |
|---|---|---|
| Detection model | Unclear / outdated | YOLOv8 (Ultralytics), actively maintained |
| OS support | Linux only | Windows, macOS, Linux |
| Setup | Manual, undocumented | `requirements.txt`, one-command setup |
| Commit history | 1 commit (zip dump) | Real, incremental commit history |
| Documentation | None | This README, with honest results and limitations |
| Evaluation | No metrics reported | Precision, recall, mAP reported and discussed |

---

## Tech stack, and why

| Component | Choice | Why |
|---|---|---|
| Detection model | YOLOv8n (Ultralytics) | Best balance of speed and accuracy for a single-object-class problem; large, active community and pretrained weights available for transfer learning |
| Language | Python | Native ecosystem for PyTorch, OpenCV, and Ultralytics — no translation layer needed |
| App framework | Streamlit | Single-file, self-contained UI + logic — no separate frontend/backend to deploy or run |
| Database | SQLite | File-based, zero server setup, appropriate for the data scale of a monitoring tool like this — not a distributed, multi-user system |
| Map | Folium (Leaflet.js under the hood) | Lightweight, Python-native, embeds directly into Streamlit |
| GPS extraction | `exifread` | Reads GPS coordinates embedded in photo EXIF metadata |
| Fast inference | ONNX Runtime | Exporting the trained model to ONNX and running at a reduced input resolution meaningfully improves CPU inference speed for live webcam use |

---

## Dataset

- **Source**: [Roboflow public pothole dataset](https://universe.roboflow.com/brad-dwyer/pothole-voxrl/dataset/1) (Brad Dwyer, `pothole-voxrl`)
- **Size**: 465 training images, 133 validation images, single class (`pothole`)
- **Format**: YOLO format (image + `.txt` bounding box annotations)

---

## Training

The model was fine-tuned from a pretrained YOLOv8n checkpoint (transfer learning) using Google Colab's free T4 GPU, since local training hardware was CPU-only.

Two training runs were done, to show real iteration rather than a single unexamined result:

| Run | Epochs | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|
| Initial pipeline test | 5 | 0.666 | 0.514 | 0.595 | 0.272 |
| Final model | 50 | 0.769 | 0.679 | 0.767 | 0.486 |

The jump between the two runs reflects both the additional epochs and the fuller dataset used in the second run. **mAP50-95 (the stricter metric) nearly doubled**, indicating the model's bounding boxes are meaningfully more accurate, not just more frequent.

---

## Real-time performance

Live webcam detection runs entirely on-device (CPU), with two optimizations applied to keep it usable:

1. **Reduced inference resolution** (416×416 instead of the default 640×640)
2. **Frame skipping** — full detection runs every 3rd frame; intermediate frames reuse the last detection result, keeping the video feed visually continuous without re-running the model on every frame

On the test hardware (Intel Core i5-13500H, no dedicated GPU), this produces noticeably smoother real-time detection than an unoptimized pipeline, though it does not reach the 30 FPS typically expected of GPU-accelerated systems.

---

## Known limitations

Documenting these honestly rather than glossing over them:

- **Not validated at highway speeds.** At 40–60 km/h, the combination of camera frame rate, CPU inference speed, and motion blur means potholes can be missed between processed frames. The system is reliable at walking pace or slow driving speeds; highway-speed reliability would require dedicated hardware (e.g. an NVIDIA Jetson) and is out of scope for this project.
- **GPS accuracy depends entirely on the source image's EXIF data.** Many images (including most of this project's own training/validation set) have no embedded GPS data at all — the app handles this gracefully but cannot invent location data that isn't present.
- **This is a detection and logging tool, not an official reporting system.** It does not submit reports to any government or municipal body. Detected data (and the map/export views) are intended to support a human decision to report an issue through proper channels, not to replace that process.
- **Single class only.** The model detects potholes as one category; it does not distinguish severity (e.g. small vs. large) or other road defects.

---

## Project structure

```
PotholeVision/
├── app.py                  # Main Streamlit application
├── detect_pothole.py       # Standalone inference script (batch testing)
├── export_onnx.py          # One-time script to export trained weights to ONNX
├── model/
│   ├── potholevision_best.pt    # Trained YOLOv8 weights
│   └── potholevision_best.onnx  # ONNX export, optimized for real-time inference
├── database/
│   └── db.py                # SQLite schema, logging, and proximity dedup logic
├── utils/
│   └── gps_extract.py       # EXIF GPS extraction helper
├── data/
│   └── pothole-dataset/     # Training dataset (train/valid/test + data.yaml)
├── requirements.txt
└── README.md
```

---

## Setup and usage

1. Clone the repository and create a virtual environment:
   ```
   git clone https://github.com/Kamalnan/PotholeVision.git
   cd PotholeVision
   python -m venv venv
   ```
2. Activate the virtual environment:
   - Windows: `.\venv\Scripts\Activate.ps1`
   - macOS/Linux: `source venv/bin/activate`
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

---

## Future work

- Severity classification (small / medium / large pothole)
- Batch video processing mode (record now, analyze later) for full-coverage road surveys at higher driving speeds
- Exportable reports (PDF/CSV) of logged detections for manual submission to relevant authorities
- Support for dedicated edge hardware for genuine highway-speed deployment
