from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from applications.models import Application

class AssistantChatTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('chatuser', password='testpass123!')
        self.client.login(username='chatuser', password='testpass123!')
        self.app = Application.objects.create(
            user=self.user,
            full_name='Ali',
            father_name='Ahmed',
            cnic_number='1234567890123',
            date_of_birth='1995-01-15',
            address='123 Main St',
            city='Lahore',
            reason='Correction',
            status='draft'
        )

    @patch('assistant.views.call_ollama')
    def test_chat_reply(self, mock_ollama):
        mock_ollama.return_value = "Your form looks good!"

        response = self.client.post(
            reverse('ask_assistant'),
            {'application_id': self.app.id, 'message': 'Check my form'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your form looks good!')
        self.assertNotContains(response, 'ERROR_FIELD:')

    @patch('assistant.views.call_ollama')
    def test_chat_error_detection(self, mock_ollama):
        mock_ollama.return_value = "ERROR_FIELD:cnic_number:CNIC must be 13 digits.\nCheck your input."

        response = self.client.post(
            reverse('ask_assistant'),
            {'application_id': self.app.id, 'message': 'Check CNIC'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CNIC must be 13 digits')
        self.assertContains(response, 'error-cnic_number')