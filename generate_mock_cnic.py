from PIL import Image, ImageDraw, ImageFont
import os

def create_mock_cnic(output_path="media/id_cards/mock_cnic.jpg"):
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)

    # Use a very common font that doesn't produce artifacts
    try:
        # DejaVu Sans is standard on Ubuntu and renders cleanly
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font = ImageFont.load_default()

    draw.text((50, 30), "PAKISTAN NATIONAL IDENTITY CARD", fill='black', font=font)

    fields = [
        ("Name:", "Ali Khan"),
        ("Father:", "Ahmed Khan"),
        ("CNIC:", "1234567890123"),
        ("Date of Birth:", "15-01-1995"),
    ]

    y = 100
    for label, value in fields:
        draw.text((50, y), label, fill='black', font=font)
        draw.text((350, y), value, fill='black', font=font)
        y += 60

    draw.rectangle([20, 20, 780, 380], outline='black', width=4)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    print(f"Mock CNIC saved to {output_path}")

if __name__ == "__main__":
    create_mock_cnic()