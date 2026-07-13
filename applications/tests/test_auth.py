from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class AuthTests(TestCase):
    def test_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

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
        self.assertRedirects(response, '/login/?next=/dashboard/')