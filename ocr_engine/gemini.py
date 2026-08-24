# ocr_engine/gemini.py
import os
import json
from django.conf import settings
from google.genai import Client

def extract_with_gemini(image_path):
    """
    Use Gemini API (google.genai) to extract structured data from an ID card image.
    Returns a dict with keys: full_name, father_name, cnic_number, date_of_birth.
    If extraction fails, returns an empty dict.
    """
    api_key = os.getenv('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return {}

    try:
        client = Client(api_key=api_key)
        prompt = """
        Extract the following fields from this CNIC image:
        - Full Name
        - Father Name
        - CNIC number (13 digits)
        - Date of Birth (format dd-mm-yyyy)
        Return a JSON object with keys: full_name, father_name, cnic_number, date_of_birth.
        If a field is not present, return an empty string for that field.
        """

        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Using gemini-2.0-flash or gemini-1.5-flash (choose available)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}]
        )

        raw_text = response.text.strip()
        if raw_text.startswith('```'):
            raw_text = raw_text.strip('`').replace('json', '', 1).strip()
        data = json.loads(raw_text)

        extracted = {
            'full_name': data.get('full_name', '').strip(),
            'father_name': data.get('father_name', '').strip(),
            'cnic_number': data.get('cnic_number', '').strip(),
            'date_of_birth': data.get('date_of_birth', '').strip(),
        }
        return extracted

    except Exception as e:
        print(f"Gemini extraction failed: {e}")
        return {}