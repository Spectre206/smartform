from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ask_assistant, name='ask_assistant'),
]