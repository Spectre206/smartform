import pytesseract
import re
from .preprocessing import preprocess_image

def extract_cnic_data(image_path):
    # Preprocess the image
    processed = preprocess_image(image_path)
    if processed is None:
        return {}

    # Use Tesseract with page segmentation mode 6 (uniform block of text)
    config = '--psm 6'
    text = pytesseract.image_to_string(processed, lang='eng', config=config)
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    data = {
        'full_name': '',
        'father_name': '',
        'cnic_number': '',
        'date_of_birth': '',
    }

    # Simple pattern matching (you can improve this later)
    for i, line in enumerate(lines):
        # Look for name after "Name" or "NAME"
        if re.search(r'\bname\b', line, re.IGNORECASE):
            if i + 1 < len(lines) and not lines[i+1].startswith(('Father', 'CNIC', 'Date')):
                data['full_name'] = lines[i+1].strip()
        # Father name
        if re.search(r'\bfather', line, re.IGNORECASE):
            if i + 1 < len(lines):
                data['father_name'] = lines[i+1].strip()
        # CNIC number: 13 digits (with or without dashes)
        cnic_match = re.search(r'\b(\d{5}-\d{7}-\d{1}|\d{13})\b', line)
        if cnic_match:
            data['cnic_number'] = cnic_match.group().replace('-', '')
        # Date of birth (dd-mm-yyyy or dd/mm/yyyy)
        dob_match = re.search(r'\d{2}[-/]\d{2}[-/]\d{4}', line)
        if dob_match:
            data['date_of_birth'] = dob_match.group().replace('/', '-')

    return data