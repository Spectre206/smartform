from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from applications.models import Application

class DeleteApplicationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('deleteuser', password='testpass123!')
        self.client.login(username='deleteuser', password='testpass123!')
        self.app = Application.objects.create(
            user=self.user,
            full_name='To Delete',
            status='draft'
        )

    def test_delete_own_application(self):
        response = self.client.post(reverse('delete_application', args=[self.app.pk]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Application.objects.filter(pk=self.app.pk).exists())

    def test_cannot_delete_other_user_application(self):
        other_user = User.objects.create_user('other', password='testpass123!')
        other_app = Application.objects.create(user=other_user, status='draft')
        response = self.client.post(reverse('delete_application', args=[other_app.pk]))
        # Should return 404 because the user doesn't own this application
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Application.objects.filter(pk=other_app.pk).exists())