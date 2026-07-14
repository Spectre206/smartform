import os
from django.conf import settings
from django.http import FileResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Application
from .forms import ApplicationForm, ImageUploadForm
from ocr_engine.extractor import extract_cnic_data


def landing(request):
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

# ---------- Authentication ----------
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# ---------- Dashboard & Applications ----------
@login_required
def dashboard(request):
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'applications': applications})

@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, "Application created. You can now upload your CNIC image.")
            return redirect('edit_application', pk=application.pk)
    else:
        form = ApplicationForm()
    return render(request, 'application_form.html', {'form': form, 'title': 'New Application'})

@login_required
def edit_application(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application updated.")
            return redirect('dashboard')
    else:
        form = ApplicationForm(instance=application)
    return render(request, 'application_form.html', {
        'form': form,
        'application': application,
        'title': 'Edit Application'
    })

#------- Delete Application -------#
@login_required
def delete_application(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        application.delete()
        messages.success(request, "Application deleted successfully.")
    return redirect('dashboard')

@login_required
def upload_cnic(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            application.id_card_image = image
            application.save()

            # Run OCR extraction
            image_path = application.id_card_image.path
            extracted = extract_cnic_data(image_path)

            # Update fields if extracted data is not empty
            if extracted.get('full_name'):
                application.full_name = extracted['full_name']
            if extracted.get('father_name'):
                application.father_name = extracted['father_name']
            if extracted.get('cnic_number'):
                application.cnic_number = extracted['cnic_number']
            if extracted.get('date_of_birth'):
                # Convert string to date object (expected format dd-mm-yyyy)
                try:
                    from datetime import datetime
                    application.date_of_birth = datetime.strptime(
                        extracted['date_of_birth'], '%d-%m-%Y'
                    ).date()
                except (ValueError, KeyError):
                    pass  # leave as is if parsing fails

            application.status = 'extracted'
            application.save()
            messages.success(request, "CNIC uploaded and data extracted.")
            return redirect('edit_application', pk=application.pk)
    else:
        form = ImageUploadForm()
    return render(request, 'upload_cnic.html', {'form': form, 'application': application})

@login_required
def validate_application(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        # Import here to keep dependencies clean
        from assistant.views import call_ollama, load_system_prompt
        import json

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

        errors = []
        for line in reply.splitlines():
            if line.startswith("ERROR_FIELD:"):
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    errors.append({'field': parts[1], 'message': parts[2].strip()})

        if errors:
            form = ApplicationForm(instance=application)
            return render(request, 'application_form.html', {
                'form': form,
                'application': application,
                'title': 'Edit Application',
                'validation_errors': errors,
            })
        else:
            application.status = 'validated'
            application.save()
            messages.success(request, "Application validated! You can now generate a PDF.")
            return redirect('edit_application', pk=application.pk)

    return redirect('edit_application', pk=application.pk)

#---------- Print Application ----------
@login_required
def generate_pdf(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)

    # Render an HTML template with application data
    html_string = render_to_string('pdf/application_pdf.html', {'application': application})

    # Generate the PDF file
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f'application_{application.pk}.pdf')
    HTML(string=html_string).write_pdf(target=pdf_path)

    # Save the file reference and update status
    application.pdf_file = f'pdfs/application_{application.pk}.pdf'
    application.status = 'pdf_ready'
    application.save()

    # Return the PDF as a downloadable file
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True,
                        filename=f'application_{application.pk}.pdf')

#---------- Validate Application ----------#
@login_required
def validate_application(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        from assistant.views import call_ollama, load_system_prompt
        import json

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

        errors = []
        for line in reply.splitlines():
            if line.startswith("ERROR_FIELD:"):
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    errors.append({'field': parts[1], 'message': parts[2].strip()})

        if errors:
            # Re-render the edit page with errors
            form = ApplicationForm(instance=application)
            return render(request, 'application_form.html', {
                'form': form,
                'application': application,
                'title': 'Edit Application',
                'validation_errors': errors,
            })
        else:
            application.status = 'validated'
            application.save()
            messages.success(request, "Application validated! You can now generate a PDF.")
            return redirect('edit_application', pk=application.pk)

    return redirect('edit_application', pk=application.pk)