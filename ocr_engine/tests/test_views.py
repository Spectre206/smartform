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

    @patch('applications.views.process_application.delay')
    def test_upload_and_extract(self, mock_delay):
        # Create a real tiny JPEG image
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

        # Check redirect
        self.assertRedirects(response, reverse('edit_application', args=[self.app.pk]))

        # Check the background task was enqueued with correct application ID
        mock_delay.assert_called_once_with(self.app.pk)

        # The application should still be in draft state (no synchronous extraction)
        self.app.refresh_from_db()
        self.assertEqual(self.app.status, 'draft')