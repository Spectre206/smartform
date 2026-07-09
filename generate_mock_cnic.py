from PIL import Image, ImageDraw, ImageFont
import os

def create_mock_cnic(output_path="media/id_cards/mock_cnic.jpg"):
    # Create a white background (400x250 pixels, RGB)
    img = Image.new('RGB', (400, 250), color='white')
    draw = ImageDraw.Draw(img)

    # Try to use a common system font; fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
        small_font = font

    # Draw a simple border
    draw.rectangle([10, 10, 390, 240], outline='black', width=2)

    # Header
    draw.text((30, 20), "PAKISTAN NATIONAL IDENTITY CARD", fill='black', font=font)
    draw.text((30, 45), "--------------------------------------------------", fill='black', font=small_font)

    # Fields (labels on left, values on right, with clear "Name:" format)
    fields = [
        ("Name:", "Ali Khan"),
        ("Father Name:", "Ahmed Khan"),
        ("CNIC Number:", "1234567890123"),
        ("Date of Birth:", "15-01-1995"),
    ]

    y = 75
    for label, value in fields:
        draw.text((30, y), label, fill='black', font=small_font)
        draw.text((180, y), value, fill='black', font=small_font)
        y += 30

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Mock CNIC saved to {output_path}")

if __name__ == "__main__":
    create_mock_cnic()