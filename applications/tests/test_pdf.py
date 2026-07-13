from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, mock_open
from applications.models import Application

class PDFGenerationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('pdfuser', password='testpass123!')
        self.client.login(username='pdfuser', password='testpass123!')
        self.app = Application.objects.create(
            user=self.user,
            full_name='Test',
            father_name='Father',
            cnic_number='1234567890123',
            date_of_birth='1995-01-15',
            address='Address',
            city='City',
            reason='Reason',
            status='validated'
        )

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('weasyprint.HTML.write_pdf')
    def test_pdf_generation(self, mock_write_pdf, mock_file_open, mock_makedirs):
        response = self.client.get(reverse('generate_pdf', args=[self.app.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.app.refresh_from_db()
        self.assertTrue(self.app.pdf_file)
        self.assertEqual(self.app.status, 'pdf_ready')