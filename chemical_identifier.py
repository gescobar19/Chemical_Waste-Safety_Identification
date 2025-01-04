from ultralytics import YOLO
from PIL import Image
import pytesseract

# Specify the path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the trained model
model = YOLO(r"C:\Users\gesco\Downloads\ChemicalIdentificationSystem\runs\detect\train9\weights\best.pt")

# Predict on an image
results = model.predict(source='benzene_chemical_example.jpg', save=True, conf=0.2)

# Process detections
for result in results:
    for box in result.boxes:
        # Extract class ID and label
        cls = int(box.cls)  # Class ID
        label = model.names[cls]  # Class name

        # Extract bounding box coordinates
        print("box.xyxy:", box.xyxy)

        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        # Crop the detected region
        image = Image.open("benzene_chemical_example.jpg")
        cropped_image = image.crop((x1, y1, x2, y2))

        # Apply OCR to extract text (if necessary)
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        extracted_text = pytesseract.image_to_string(cropped_image)
        print(f"Detected {label}: {extracted_text.strip()}")

