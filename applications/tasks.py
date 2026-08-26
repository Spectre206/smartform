# applications/tasks.py
from celery import shared_task
from django.contrib.auth.models import User
from .models import Application
from ocr_engine.extractor import extract_cnic_data
from assistant.views import call_ollama, load_system_prompt
import json

@shared_task
def process_application(application_id):
    """
    Background task:
    1. Extract data from uploaded CNIC image (Gemini → Tesseract fallback).
    2. Update Application fields.
    3. Set status to 'extracted'.
    4. Run AI validation.
    5. If no errors, set status to 'validated'.
    """
    try:
        application = Application.objects.get(pk=application_id)
    except Application.DoesNotExist:
        return "Application not found"

    # 1. Extraction
    image_path = application.id_card_image.path
    extracted = extract_cnic_data(image_path)
    
    # 2. Update fields (only if extracted value is not empty)
    if extracted.get('full_name'):
        application.full_name = extracted['full_name']
    if extracted.get('father_name'):
        application.father_name = extracted['father_name']
    if extracted.get('cnic_number'):
        application.cnic_number = extracted['cnic_number']
    if extracted.get('date_of_birth'):
        from datetime import datetime
        try:
            application.date_of_birth = datetime.strptime(
                extracted['date_of_birth'], '%d-%m-%Y'
            ).date()
        except (ValueError, KeyError):
            pass  # leave as is if parsing fails
    if extracted.get('address'):
        application.address = extracted['address']
    if extracted.get('city'):
        application.city = extracted['city']
    # 3. Set initial status after extraction
    application.status = 'extracted'
    application.save()

    # 4. AI validation
    form_data = {
        "full_name": application.full_name,
        "father_name": application.father_name,
        "cnic_number": application.cnic_number,
        "date_of_birth": str(application.date_of_birth) if application.date_of_birth else "",
        "address": application.address,
        "city": application.city,
        "reason": application.reason,
    }
    system_prompt = load_system_prompt().replace("{form_data}", json.dumps(form_data))
    full_prompt = f"{system_prompt}\n\nUser: Check this form for errors.\nAssistant:"
    reply = call_ollama(full_prompt)

        # Parse any ERROR_FIELD markers
    errors = []
    if reply and 'ERROR_FIELD:' in reply:
        for line in reply.splitlines():
            if line.startswith("ERROR_FIELD:"):
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    errors.append(parts[1])

    # If no AI errors, fallback to Django validation to be safe
    if not errors:
        from .forms import ApplicationForm
        form = ApplicationForm({
            'full_name': application.full_name,
            'father_name': application.father_name,
            'cnic_number': application.cnic_number,
            'date_of_birth': application.date_of_birth,
            'address': application.address,
            'city': application.city,
            'reason': application.reason,
        })
        if form.is_valid():
            application.status = 'validated'
            application.save()
            return f"Application {application.id} validated successfully (Django fallback)"
        else:
            # Keep as extracted, but you could store form errors if needed
            return f"Application {application.id} extracted but invalid according to Django"
    else:
        # AI found errors, keep extracted
        application.status = 'extracted'
        application.save()
        return f"Application {application.id} extracted but has errors: {errors}"