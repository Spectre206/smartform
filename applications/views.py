from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Application
from .forms import ApplicationForm

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
            if application.status != 'draft':
                application.status = 'draft'
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