from PIL import Image, ImageDraw, ImageFont
import os

def create_mock_cnic(output_path="media/id_cards/mock_cnic.jpg"):
    img = Image.new('RGB', (800, 500), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font = ImageFont.load_default()

    draw.text((50, 30), "PAKISTAN NATIONAL IDENTITY CARD", fill='black', font=font)

    fields = [
    ("Name:", "Ali Khan"),
    ("Father:", "Ahmed Khan"),
    ("CNIC:", "1234567890123"),
    ("Date of Birth:", "15-01-1995"),
    ("Address:", "123 Main Street, Lahore"),
    ("City:", "Lahore"),
]

    y = 100
    for label, value in fields:
        draw.text((50, y), label, fill='black', font=font)
        draw.text((400, y), value, fill='black', font=font)   # increased x offset
        y += 70   # more vertical spacing

    draw.rectangle([20, 20, 780, 480], outline='black', width=4)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    print(f"Mock CNIC saved to {output_path}")

if __name__ == "__main__":
    create_mock_cnic()