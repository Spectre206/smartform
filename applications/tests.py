from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
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

