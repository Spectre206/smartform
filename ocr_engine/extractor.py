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
                # Find all words to the right (within 30px vertically)
                                # Only consider words on the SAME line (vertical diff < 10)
                same_line = [
                    other for other in words
                    if abs(other['y'] - w['y']) < 10 and other['x'] > w['x']
                ]
                if same_line:
                    same_line.sort(key=lambda o: o['x'])
                    # First candidate starts the value
                    value_words = [same_line[0]['original']]
                    last_x = same_line[0]['x'] + same_line[0]['w']
                    # Collect following words horizontally close
                    for cand in same_line[1:]:
                        if cand['x'] - last_x < 40:
                            value_words.append(cand['original'])
                            last_x = cand['x'] + cand['w']
                        else:
                            break
                    value = ' '.join(value_words)
                    if regex:
                        match = re.search(regex, value)
                        if match:
                            value = match.group()
                    extracted[field] = value
                break

    # Fallback: search full text for patterns not found via label
    full_text = ' '.join(w['original'] for w in words)

    if not extracted['cnic_number']:
        match = re.search(CNIC_TEMPLATE['cnic_number']['regex'], full_text)
        if match:
            extracted['cnic_number'] = match.group().replace('-', '')

    if not extracted['date_of_birth']:
        match = re.search(r'\b\d{2}[-/]\d{2}[-/]\d{4}\b', full_text)
        if match:
            extracted['date_of_birth'] = match.group().replace('/', '-')

    # Normalise date
    if extracted['date_of_birth']:
        try:
            datetime.strptime(extracted['date_of_birth'], '%d-%m-%Y')
        except ValueError:
            extracted['date_of_birth'] = ''
        # Clean up stray quotes or backticks
    for key in extracted:
        extracted[key] = extracted[key].strip("`'‘’\"")

    return extracted