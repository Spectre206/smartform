from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch
from applications.models import Application
from applications.tasks import process_application

class ProcessApplicationTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('taskuser', password='testpass123!')
        self.app = Application.objects.create(user=self.user, status='draft')
        # Dummy image
        from PIL import Image
        import io
        img = Image.new('RGB', (10, 10), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        self.app.id_card_image.save('test.jpg', img_byte_arr)
        self.app.save()

    @patch('applications.tasks.call_ollama')
    @patch('applications.tasks.extract_cnic_data')
    def test_full_flow_success(self, mock_extract, mock_ollama):
        mock_extract.return_value = {
            'full_name': 'Test Name',
            'father_name': 'Father Name',
            'cnic_number': '1234567890123',
            'date_of_birth': '15-01-1995',
        }
        mock_ollama.return_value = "Your form looks good."

        result = process_application(self.app.pk)
        self.app.refresh_from_db()

        self.assertEqual(self.app.full_name, 'Test Name')
        self.assertEqual(self.app.father_name, 'Father Name')
        self.assertEqual(self.app.cnic_number, '1234567890123')
        self.assertEqual(str(self.app.date_of_birth), '1995-01-15')
        self.assertEqual(self.app.status, 'validated')
        self.assertIn('validated', result)

    @patch('applications.tasks.call_ollama')
    @patch('applications.tasks.extract_cnic_data')
    def test_flow_with_errors(self, mock_extract, mock_ollama):
        mock_extract.return_value = {
            'full_name': 'Test',
            'father_name': '',
            'cnic_number': '123',
            'date_of_birth': '',
        }
        mock_ollama.return_value = "ERROR_FIELD:cnic_number:CNIC must be 13 digits."

        result = process_application(self.app.pk)
        self.app.refresh_from_db()

        self.assertEqual(self.app.status, 'extracted')
        self.assertIn('errors', result)