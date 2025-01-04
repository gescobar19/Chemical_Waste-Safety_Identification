# Import YOLO from ultralytics
from ultralytics import YOLO

# Load the YOLOv8 model
# Replace 'yolov8n.pt' with your preferred model variant ('yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', etc.)
model = YOLO('yolov8s.pt')

# Train the model
# Specify the dataset, number of epochs, and enable data augmentation
model.train(
    data=r'C:\Users\gesco\Downloads\ChemicalIdentificationSystem\datasets\GHSSymbols.v2i.yolov8\data.yaml',       # Path to the data.yaml file
    epochs=50,              # Number of training epochs
    batch=16,               # Batch size (adjust based on your GPU memory)
    imgsz=640,              # Image size (640x640 is standard for YOLOv8)
    augment=True,           # Enable data augmentation
    device='cpu',               # Specify GPU (0) or CPU ('cpu')
    val=True  
)
