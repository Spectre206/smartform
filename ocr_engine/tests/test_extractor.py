from django.test import SimpleTestCase
from unittest.mock import patch
from ocr_engine.extractor import extract_cnic_data
import numpy as np
import cv2

class TestOCRExtractor(SimpleTestCase):
    @patch('ocr_engine.extractor.pytesseract.image_to_data')
    @patch('ocr_engine.extractor.preprocess_image')
    def test_extract_all_fields(self, mock_preprocess, mock_tesseract):
        # Mock a preprocessed image (just a dummy)
        mock_preprocess.return_value = np.zeros((100, 100), dtype=np.uint8)

        # Mock word data simulating a CNIC layout
        mock_tesseract.return_value = {
            'level': [5]*6,
            'page_num': [1]*6,
            'block_num': [1]*6,
            'par_num': [1]*6,
            'line_num': [1]*6,
            'word_num': [1]*6,
            'left': [10, 120, 10, 130, 10, 120],
            'top': [10, 10, 30, 30, 50, 50],
            'width': [50, 100, 60, 90, 40, 100],
            'height': [15, 15, 15, 15, 15, 15],
            'conf': [90]*6,
            'text': ['Name:', 'Ali Khan', 'Father:', 'Ahmed Khan',
                     'CNIC:', '1234567890123'],
        }
        result = extract_cnic_data('fake_path.jpg')
        self.assertEqual(result['full_name'], 'Ali Khan')
        self.assertEqual(result['father_name'], 'Ahmed Khan')
        self.assertEqual(result['cnic_number'], '1234567890123')

    # Add test for missing fields, etc.