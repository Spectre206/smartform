# ocr_engine/extractor.py
import pytesseract
import re
from datetime import datetime
from .preprocessing import preprocess_image

# Extraction template for CNIC
CNIC_TEMPLATE = {
    "full_name": {"label": "name", "direction": "right"},
    "father_name": {"label": "father", "direction": "right"},
    "cnic_number": {"label": "cnic", "direction": "right", "regex": r"\b\d{5}-?\d{7}-?\d\b|\b\d{13}\b"},
    "date_of_birth": {"label": "birth", "direction": "right",
                      "regex": r"\b\d{2}[-/]\d{2}[-/]\d{4}\b"},
}

def extract_cnic_data(image_path):
    processed = preprocess_image(image_path)
    if processed is None:
        return {}

    data = pytesseract.image_to_data(
        processed,
        lang='eng',
        config='--psm 6',
        output_type=pytesseract.Output.DICT
    )

    # Build list of words with coordinates
    words = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text:
            words.append({
                'text': text.lower(),
                'original': data['text'][i],
                'x': data['left'][i],
                'y': data['top'][i],
                'w': data['width'][i],
                'h': data['height'][i],
            })

    extracted = {key: '' for key in CNIC_TEMPLATE}

    for field, config in CNIC_TEMPLATE.items():
        label = config['label']
        regex = config.get('regex', None)

        for i, w in enumerate(words):
            if label in w['text']:
                # Find the closest word to the right (within 20px vertically)
                candidates = [
                    other for other in words
                    if other['x'] > w['x'] and abs(other['y'] - w['y']) < 20
                ]
                if candidates:
                    nearest = min(candidates, key=lambda o: o['x'])
                    value = nearest['original']
                    if regex:
                        match = re.search(regex, value)
                        if match:
                            value = match.group()
                    extracted[field] = value
                break

    # Fallback for CNIC number: search whole text
    if not extracted['cnic_number']:
        full_text = ' '.join(w['original'] for w in words)
        match = re.search(CNIC_TEMPLATE['cnic_number']['regex'], full_text)
        if match:
            extracted['cnic_number'] = match.group().replace('-', '')

    # Normalise date
    if extracted['date_of_birth']:
        date_str = extracted['date_of_birth'].replace('/', '-')
        try:
            datetime.strptime(date_str, '%d-%m-%Y')
            extracted['date_of_birth'] = date_str
        except ValueError:
            extracted['date_of_birth'] = ''

    return extracted