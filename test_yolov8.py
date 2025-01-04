from ultralytics import YOLO

# Load a model
model = YOLO("C:/Users/gesco/Downloads/ChemicalIdentificationSystem/runs/detect/train9/weights/best.pt")

# Run predictions
results = model.predict(source="C:/Users/gesco/Downloads/ChemicalIdentificationSystem/datasets/GHSSymbols.v2i.yolov8/test/images", save=True, conf=0.2)

# Print results
print(results)
