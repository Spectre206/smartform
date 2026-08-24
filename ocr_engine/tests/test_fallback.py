from django.test import SimpleTestCase
from unittest.mock import patch
from ocr_engine.extractor import extract_cnic_data

class TestOCRFallback(SimpleTestCase):
    @patch('ocr_engine.extractor.extract_with_gemini')
    @patch('ocr_engine.extractor.extract_with_tesseract')
    def test_gemini_used_when_success(self, mock_tesseract, mock_gemini):
        mock_gemini.return_value = {
            'full_name': 'Gemini Name',
            'father_name': 'Gemini Father',
            'cnic_number': '1234567890123',
            'date_of_birth': '01-01-1990',
        }
        result = extract_cnic_data('fake_path.jpg')
        self.assertEqual(result['full_name'], 'Gemini Name')
        mock_tesseract.assert_not_called()

    @patch('ocr_engine.extractor.extract_with_gemini')
    @patch('ocr_engine.extractor.extract_with_tesseract')
    def test_tesseract_fallback_when_gemini_empty(self, mock_tesseract, mock_gemini):
        mock_gemini.return_value = {}
        mock_tesseract.return_value = {
            'full_name': 'Tess Name',
            'father_name': 'Tess Father',
            'cnic_number': '1234567890123',
            'date_of_birth': '02-02-1992',
        }
        result = extract_cnic_data('fake_path.jpg')
        self.assertEqual(result['full_name'], 'Tess Name')
        mock_tesseract.assert_called_once()