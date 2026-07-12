from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from PIL import Image
import io
from applications.models import Application

class OCRUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ocruser', password='testpass123!')
        self.client.login(username='ocruser', password='testpass123!')
        self.app = Application.objects.create(user=self.user, status='draft')

    def test_upload_cnic_view_get(self):
        response = self.client.get(reverse('upload_cnic', args=[self.app.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload_cnic.html')

    @patch('applications.views.extract_cnic_data')
    def test_upload_and_extract(self, mock_extract):
        mock_extract.return_value = {
            'full_name': 'Test Name',
            'father_name': 'Father Name',
            'cnic_number': '1234567890123',
            'date_of_birth': '15-01-1995',
        }

        img = Image.new('RGB', (1, 1), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        image = SimpleUploadedFile(
            "test_cnic.jpg",
            img_byte_arr.read(),
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_cnic', args=[self.app.pk]),
            {'image': image}
        )

        self.assertRedirects(response, reverse('edit_application', args=[self.app.pk]))
        self.app.refresh_from_db()
        self.assertEqual(self.app.full_name, 'Test Name')
        self.assertEqual(self.app.cnic_number, '1234567890123')
        self.assertEqual(self.app.date_of_birth.strftime('%Y-%m-%d'), '1995-01-15')
        self.assertEqual(self.app.status, 'extracted')