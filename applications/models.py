from django.db import models
from django.contrib.auth.models import User

class Application(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('extracted', 'Extracted'),
        ('validated', 'Validated'),
        ('pdf_ready', 'PDF Ready'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=100, default="CNIC Correction")
    full_name = models.CharField(max_length=100, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    cnic_number = models.CharField(max_length=13, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    id_card_image = models.ImageField(upload_to='id_cards/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True)

    def __str__(self):
        return f"Application #{self.id} - {self.user.username}"