import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from transformers import BartTokenizer, BartForConditionalGeneration
import re
from PIL import Image
from ultralytics import YOLO
import os
import requests
import pytesseract
import cv2
from transformers import pipeline

# Path to Tesseract executable (adjust based on your installation)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize YOLOv8 model
yolo_model = YOLO("C:/Users/gesco/Downloads/ChemicalIdentificationSystem/runs/detect/train9/weights/best.pt")  # Replace with your trained model path

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(r"C:\Users\gesco\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")  # Update with your path to chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Initialize BART model and tokenizer
#model_name = "facebook/bart-large-cnn"
#tokenizer = BartTokenizer.from_pretrained(model_name)
#model = BartForConditionalGeneration.from_pretrained(model_name)

summarizer = pipeline("summarization")

def format_bullet_points(text: str) -> str:
    sentences = text.split(".")
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    bullet_points = "\n- ".join(sentences)
    return f"- {bullet_points}"


def get_cid(chemical_name):
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
    url = f"{base_url}{chemical_name}/cids/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cid = data['IdentifierList']['CID'][0]
            return cid
        else:
            print(f"Error fetching CID for {chemical_name}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching CID: {e}")
        return None
    
# Adjust the summarize_text function with more targeted prompt templates
def summarize_text(text, prompt_template):
    #prompt template was used for previous llm, not needed for this summarizer
    summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
    summary = summarizer("Summarize the key points: " + text)
    print(summary[0]['summary_text'])
    return format_bullet_points(summary[0]['summary_text'])


# Adjusted clean_summary to handle more patterns and improve text removal
def clean_summary(summary: str) -> str:
    summary = re.sub(r"http[s]?://\S+", "", summary)  # Remove URLs
    summary = re.sub(r"(Sigma-Aldrich|HSDB|EPA|CFR|United Nations|Material Safety Data Sheet|Data Sheet).*?(\.|$)", "", summary, flags=re.IGNORECASE)  # Remove references
    summary = re.sub(r"(Product Number: \d+|Version \d+\.\d+).*?(\.|$)", "", summary)  # Remove product numbers
    summary = re.sub(r"(\bAcetone\b\s?\(\d+\s?total\))", "Acetone", summary)  # Normalize chemical names
    summary = re.sub(r"\s{2,}", " ", summary).strip()  # Remove extra spaces
    # Remove repetitive sections
    summary = re.sub(r"\n- \s*-", "\n-", summary)
    return summary

# Adjust the prompt templates for the specific sections
def scrape_and_summarize(chemical_name):
    cid = get_cid(chemical_name)
    print(f"Detected Chemical: {chemical_name}, CID: {cid}")

    if not cid:
        return "CID not found.", "CID not found."
    
    url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}#section=Safety-and-Hazards"
    print(f"Constructed URL: {url}")
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        
        # Scrape "Disposal Methods"
        try:
            disposal_section = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "Disposal-Methods"))
            )
            disposal_divs = disposal_section.find_elements(By.CSS_SELECTOR, "div.break-words.space-y-1")
            disposal_content = "\n".join([div.text for div in disposal_divs if div.text.strip()])
            
            if disposal_content.strip():
                disposal_summary = summarize_text(disposal_content, f"Summarize the detailed disposal methods for {chemical_name}, focusing on steps and safety considerations.")
                cleaned_disposal_summary = clean_summary(disposal_summary)
            else:
                cleaned_disposal_summary = "Disposal Methods section not found for this chemical."
        except Exception as e:
            cleaned_disposal_summary = f"Disposal Methods section not found: {e}"
        
        # Scrape "Preventive Measures"
        try:
            preventive_section = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "Preventive-Measures"))
            )
            preventive_content = preventive_section.get_attribute('innerText')
            
            if preventive_content.strip():
                preventive_summary = summarize_text(preventive_content, f"Provide preventive measures for handling {chemical_name}, including safety protocols and hazard mitigation.")
                cleaned_preventive_summary = clean_summary(preventive_summary)
            else:
                cleaned_preventive_summary = "Preventive Measures section not found for this chemical."
        except Exception as e:
            cleaned_preventive_summary = f"Preventive Measures section not found: {e}"
    
    except Exception as e:
        cleaned_disposal_summary = f"An error occurred while retrieving data: {e}"
        cleaned_preventive_summary = ""
    
    print("Disposal Summary:\n" + cleaned_disposal_summary + "\n===================\n" + "Preventive summary:\n" + cleaned_preventive_summary)
    return cleaned_disposal_summary, cleaned_preventive_summary

# Function to Detect Chemical Names using YOLOv8
def detect_and_read_chemical(image_path):
    # Load YOLOv8 model
    results = yolo_model(image_path)
    detected_chemicals = []  # List to store detected chemicals

    # Load the original image
    original_image = cv2.imread(image_path)

    for result in results:
        for box in result.boxes:
            # Extract class ID and label
            cls = int(box.cls)  # Class ID
            label = yolo_model.names[cls].strip().lower()
            print(f"Checking condition for detected label: '{label}'")  # Universal debug statement
            
            if label == "chemical name":
                print("Condition satisfied: Detected 'chemical name'.")
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                print(f"Bounding Box: x1={x1}, y1={y1}, x2={x2}, y2={y2}")  # Debug bounding box
                
                # Ensure bounding box is within image dimensions
                height, width, _ = original_image.shape
                if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
                    print("Bounding box coordinates out of image bounds.")
                    continue
                
                # Crop the detected region
                cropped_region = original_image[y1:y2, x1:x2]
                
                # Save cropped region for debugging
                debug_path = f"debug_crop_{x1}_{y1}.png"
                pil_image = Image.fromarray(cv2.cvtColor(cropped_region, cv2.COLOR_BGR2RGB))
                pil_image.save(debug_path)
                print(f"Cropped region saved for inspection: {debug_path}")
                
                # Perform OCR
                text = pytesseract.image_to_string(pil_image, config='--psm 6').strip()
                print(f"OCR Result: '{text}'")
                
                if text:
                    detected_chemicals.append(text)
            else:
                print(f"Condition failed: '{label}' does not match 'chemical name'.")

    # Remove duplicates and return
    detected_chemicals = list(set(detected_chemicals))
    return detected_chemicals

# Tkinter GUI Function
def select_image_and_process():
    image_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
    )
    
    if not image_path:
        return
    
    # Detect and read chemical names using YOLOv8 and OCR
    chemical_names = detect_and_read_chemical(image_path)
    
    if not chemical_names:
        messagebox.showwarning("No Detection", "No chemical names detected in the image.")
        return
    
    # Use the first detected chemical name
    chemical_name = chemical_names[0]
    
    # Scrape and summarize information for the detected chemical
    disposal_summary, preventive_summary = scrape_and_summarize(chemical_name)
    
    # Update UI
    disposal_summary_text.config(state=tk.NORMAL)
    disposal_summary_text.delete(1.0, tk.END)
    disposal_summary_text.insert(tk.END, disposal_summary)
    disposal_summary_text.config(state=tk.DISABLED)
    
    preventive_summary_text.config(state=tk.NORMAL)
    preventive_summary_text.delete(1.0, tk.END)
    preventive_summary_text.insert(tk.END, preventive_summary)
    preventive_summary_text.config(state=tk.DISABLED)
    
    disposal_label.config(text=f"Disposal Methods Summary for {chemical_name}:")
    preventive_label.config(text=f"Preventive Measures Summary for {chemical_name}:")


# Create the Tkinter window
root = tk.Tk()
root.title("Chemical Safety Summaries")

# Set up window size
root.geometry("800x700")

# Create frames for layout
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Button to select image
select_button = tk.Button(frame, text="Select Image", command=select_image_and_process, font=("Helvetica", 12))
select_button.pack(pady=(0, 20))

# Disposal Methods Section
disposal_label = tk.Label(frame, text="Disposal Methods Summary:", font=("Helvetica", 14, "bold"))
disposal_label.pack(pady=(0, 10))

disposal_summary_text = tk.Text(frame, height=10, width=80, wrap=tk.WORD)
disposal_summary_text.insert(tk.END, "")
disposal_summary_text.config(state=tk.DISABLED)  # Make the text widget read-only
disposal_summary_text.pack(pady=(0, 20))

# Preventive Measures Section
preventive_label = tk.Label(frame, text="Preventive Measures Summary:", font=("Helvetica", 14, "bold"))
preventive_label.pack(pady=(0, 10))

preventive_summary_text = tk.Text(frame, height=10, width=80, wrap=tk.WORD)
preventive_summary_text.insert(tk.END, "")
preventive_summary_text.config(state=tk.DISABLED)  # Make the text widget read-only
preventive_summary_text.pack()

# Run the Tkinter event loop
root.mainloop()
