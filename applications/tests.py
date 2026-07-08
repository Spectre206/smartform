from PIL import Image
import io
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Application

class ApplicationFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpass123!')
        self.client.login(username='testuser', password='testpass123!')

    def test_create_application_view(self):
        response = self.client.get(reverse('create_application'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_form.html')

        data = {
            'full_name': 'Ali Khan',
            'father_name': 'Ahmed Khan',
            'cnic_number': '1234567890123',
            'date_of_birth': '1995-01-15',
            'address': '123 Main St',
            'city': 'Lahore',
            'reason': 'Correction in name'
        }
        response = self.client.post(reverse('create_application'), data)
        self.assertEqual(response.status_code, 302)  # redirect to edit
        app = Application.objects.first()
        self.assertEqual(app.full_name, 'Ali Khan')
        self.assertEqual(app.status, 'draft')

    def test_edit_application_view(self):
        app = Application.objects.create(user=self.user, full_name='Old Name', status='draft')
        response = self.client.get(reverse('edit_application', args=[app.pk]))
        self.assertEqual(response.status_code, 200)

        # Update data
        data = {
            'full_name': 'New Name',
            'father_name': 'Father',
            'cnic_number': '1234567890123',
            'date_of_birth': '1995-01-15',
            'address': 'Address',
            'city': 'City',
            'reason': 'Reason'
        }
        response = self.client.post(reverse('edit_application', args=[app.pk]), data)
        self.assertRedirects(response, reverse('dashboard'))
        app.refresh_from_db()
        self.assertEqual(app.full_name, 'New Name')

    def test_cnic_validation(self):
        data = {
            'full_name': 'Ali',
            'father_name': 'Father',
            'cnic_number': '1234',  # invalid
            'date_of_birth': '1995-01-15',
            'address': 'Address',
            'city': 'City',
            'reason': 'Reason'
        }
        response = self.client.post(reverse('create_application'), data)
        self.assertEqual(response.status_code, 200)  # stays on form
        self.assertFormError(response.context['form'], 'cnic_number', "CNIC must be exactly 13 digits.")

    def test_dashboard_shows_applications(self):
        Application.objects.create(user=self.user, full_name='Ali', status='draft')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'Ali')
        self.assertContains(response, 'Draft')

class AuthTests(TestCase):
    def test_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

        # Post valid data
        data = {
            'username': 'testuser',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_view(self):
        User.objects.create_user('testuser', password='ComplexPass123!')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        # Post login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'ComplexPass123!',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_logout_view(self):
        User.objects.create_user('testuser', password='ComplexPass123!')
        self.client.login(username='testuser', password='ComplexPass123!')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/')

#------OCR TestCases -------#
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

        self.assertRedirects(response, reverse('edit_application', args=[self.app.pk]))
        self.app.refresh_from_db()
        self.assertEqual(self.app.full_name, 'Test Name')
        self.assertEqual(self.app.cnic_number, '1234567890123')
        self.assertEqual(self.app.date_of_birth.strftime('%Y-%m-%d'), '1995-01-15')
        self.assertEqual(self.app.status, 'extracted')