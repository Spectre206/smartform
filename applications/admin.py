from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service_type', 'status', 'created_at')
    list_filter = ('status', 'service_type')
    search_fields = ('full_name', 'cnic_number')