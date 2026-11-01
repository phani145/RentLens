"""
Generates sample inspection photographs for testing RentLens AI.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def generate_sample_images():
    out_dir = os.path.dirname(__file__)
    os.makedirs(out_dir, exist_ok=True)

    # 1. Under-Sink Moisture Hazard Sample
    img1 = Image.new("RGB", (640, 480), color="#D8D0C5")
    draw = ImageDraw.Draw(img1)
    
    # Draw cabinet frame
    draw.rectangle([20, 20, 620, 460], outline="#5A4A3A", width=8)
    # Draw floor of cabinet
    draw.rectangle([28, 380, 612, 452], fill="#A89F91")
    # Draw water pipe / P-trap
    draw.rectangle([280, 40, 320, 240], fill="#8A8A8A")
    draw.ellipse([270, 220, 370, 330], outline="#7A7A7A", width=18)
    draw.rectangle([340, 240, 370, 390], fill="#8A8A8A")
    # Draw water stain on wall
    draw.ellipse([140, 260, 260, 360], fill="#6B5B4D")
    draw.text((150, 300), "Moisture Staining", fill="#FFFFFF")
    # Draw label banner
    draw.rectangle([30, 30, 280, 70], fill="#1F4E46")
    draw.text((45, 42), "TEST SAMPLE: Under-Sink Vanity", fill="#FFFFFF")

    path1 = os.path.join(out_dir, "sample_undersink_damage.jpg")
    img1.save(path1, "JPEG", quality=90)
    print("Saved sample image 1:", path1)

    # 2. Clean Living Room Sample
    img2 = Image.new("RGB", (640, 480), color="#F4F3EF")
    draw2 = ImageDraw.Draw(img2)
    # Hardwood floor
    draw2.rectangle([0, 340, 640, 480], fill="#C49A6C")
    for y in range(350, 480, 25):
        draw2.line([0, y, 640, y], fill="#B08355", width=2)
    # Window
    draw2.rectangle([200, 80, 440, 300], fill="#E6F2F7", outline="#FFFFFF", width=10)
    draw2.line([320, 80, 320, 300], fill="#FFFFFF", width=6)
    draw2.line([200, 190, 440, 190], fill="#FFFFFF", width=6)
    # Clean room banner
    draw2.rectangle([30, 30, 260, 70], fill="#1F4E46")
    draw2.text((45, 42), "TEST SAMPLE: Clean Living Room", fill="#FFFFFF")

    path2 = os.path.join(out_dir, "sample_clean_room.jpg")
    img2.save(path2, "JPEG", quality=90)
    print("Saved sample image 2:", path2)

if __name__ == "__main__":
    generate_sample_images()
