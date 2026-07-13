from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from applications.models import Application

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
        self.assertEqual(response.status_code, 302)
        app = Application.objects.first()
        self.assertEqual(app.full_name, 'Ali Khan')
        self.assertEqual(app.status, 'draft')

    def test_edit_application_view(self):
        app = Application.objects.create(user=self.user, full_name='Old Name', status='draft')
        response = self.client.get(reverse('edit_application', args=[app.pk]))
        self.assertEqual(response.status_code, 200)

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
            'cnic_number': '1234',
            'date_of_birth': '1995-01-15',
            'address': 'Address',
            'city': 'City',
            'reason': 'Reason'
        }
        response = self.client.post(reverse('create_application'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'cnic_number', "CNIC must be exactly 13 digits.")

    def test_dashboard_shows_applications(self):
        Application.objects.create(user=self.user, full_name='Ali', status='draft')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'Ali')
        self.assertContains(response, 'Draft')