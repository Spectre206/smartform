from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),                          
    path('dashboard/', views.dashboard, name='dashboard'),            
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('application/new/', views.create_application, name='create_application'),
    path('application/<int:pk>/edit/', views.edit_application, name='edit_application'),
    path('application/<int:pk>/upload/', views.upload_cnic, name='upload_cnic'),
    path('application/<int:pk>/pdf/', views.generate_pdf, name='generate_pdf'),
    path('application/<int:pk>/validate/', views.validate_application, name='validate_application'),
]