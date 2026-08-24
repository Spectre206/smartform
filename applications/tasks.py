from celery import shared_task
from .models import Application

@shared_task
def sample_task(application_id):
    application = Application.objects.get(pk=application_id)
    application.status = 'extracted'
    application.save()
    return application.status