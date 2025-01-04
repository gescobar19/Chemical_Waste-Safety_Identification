from PIL import Image, ImageDraw, ImageFont
import os

# Paths
symbols_dir = r"C:\Users\gesco\Downloads\ChemicalIdentificationSystem\ghs_symbols_dataset"  # Folder containing GHS symbols
output_dir = r"C:\Users\gesco\Downloads\ChemicalIdentificationSystem\generated_labels"   # Folder to save generated labels
os.makedirs(output_dir, exist_ok=True)

# Font for text (update the path as needed)
font = ImageFont.truetype("arial.ttf", size=15)

# Desired background size for symbols
background_size = (256, 256)
max_symbol_size = (100, 100)  # Maximum size for the symbol within the white background

# Data for synthetic labels
labels_data = [
    {
        "symbol": "flammable.jpg",
        "chemical_name": "Acetone",
        "cas_number": "67-64-1",
        "warning_text": "Highly flammable liquid and vapor. Keep away from heat and open flames."
    },
    {
        "symbol": "corrosive.jpg",
        "chemical_name": "Sulfuric Acid",
        "cas_number": "7664-93-9",
        "warning_text": "Causes severe skin burns and eye damage. Avoid contact with skin and eyes."
    },
    {
        "symbol": "gas_cylinder.jpg",
        "chemical_name": "Chlorine Gas",
        "cas_number": "7782-50-5",
        "warning_text": "Fatal if inhaled. Causes severe skin burns and eye damage."
    },
    {
        "symbol": "oxidizer.jpg",
        "chemical_name": "Hydrogen Peroxide (30%)",
        "cas_number": "7722-84-1",
        "warning_text": "May intensify fire. Causes severe skin burns and eye damage."
    },
    {
        "symbol": "health_hazard.jpg",
        "chemical_name": "Benzene",
        "cas_number": "71-43-2",
        "warning_text": "May cause cancer. Highly flammable liquid and vapor."
    },
    {
        "symbol": "corrosive.jpg",
        "chemical_name": "Sodium Hydroxide",
        "cas_number": "1310-73-2",
        "warning_text": "Causes severe skin burns and eye damage. Avoid contact with skin and eyes."
    },
    {
        "symbol": "skull_and_crossbones.jpg",
        "chemical_name": "Methanol",
        "cas_number": "67-56-1",
        "warning_text": "Highly flammable liquid and vapor. Toxic if swallowed, inhaled, or in contact with skin."
    },
    {
        "symbol": "corrosive.jpg",
        "chemical_name": "Formaldehyde",
        "cas_number": "50-00-0",
        "warning_text": "May cause cancer. Causes skin irritation and serious eye damage."
    },
    {
        "symbol": "gas_cylinder.jpg",
        "chemical_name": "Ammonia (Anhydrous)",
        "cas_number": "7664-41-7",
        "warning_text": "Toxic if inhaled. Causes severe skin burns and eye damage."
    },
    {
        "symbol": "flammable.jpg",
        "chemical_name": "Toluene",
        "cas_number": "108-88-3",
        "warning_text": "Highly flammable liquid and vapor. May cause damage to the nervous system through prolonged exposure."
    }
]


# Generate Labels
for idx, label_data in enumerate(labels_data):
    # Load GHS symbol
    symbol_path = os.path.join(symbols_dir, label_data["symbol"])
    symbol = Image.open(symbol_path).convert("RGBA")  # Ensure transparency support

    # Resize the symbol while maintaining aspect ratio
    symbol.thumbnail(max_symbol_size, Image.Resampling.LANCZOS)   # Resize to fit within max dimensions

    # Create a white background for the symbol
    background = Image.new("RGBA", background_size, "white")

    # Calculate position to center the symbol on the background
    x_offset = (background_size[0] - symbol.width) // 4
    y_offset = (background_size[1] - symbol.height) // 4
    background.paste(symbol, (x_offset, y_offset), symbol)

    # Create a larger canvas for the label (symbol + text)
    label = Image.new("RGBA", (400, 300), "white")
    draw = ImageDraw.Draw(label)

    # Paste the resized symbol onto the label canvas
    label.paste(background, (5, 5), background)

    # Add chemical name
    font = ImageFont.truetype("arialbd.ttf", size=20)  
    draw.text((170, 40), f"{label_data['chemical_name']}", fill="black", font=font)

   # Add CAS number
    font = ImageFont.truetype("arial.ttf", size=15)


    draw.text((170, 80), f"CAS: {label_data['cas_number']}", fill="blue", font=font)

    font = ImageFont.load_default()
   # Format warning text to add a new line after every period
    formatted_warning = label_data["warning_text"].replace(". ", ".\n")

    # Draw text on the label
    draw.text((140, 120), f"{formatted_warning}", fill="red", font=font)

    # Save the label
    label_name = f"label_{idx}_{label_data['chemical_name'].replace(' ', '_')}.png"
    label.save(os.path.join(output_dir, label_name))
    print(f"Generated: {label_name}")
