from django.contrib import admin
from .models import Worker, Job, Application

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'full_name', 'phone_number', 'age', 'is_blacklisted', 'created_at')
    search_fields = ('full_name', 'phone_number')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('unical_id', 'title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('unical_id', 'title')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('worker', 'job', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('worker__full_name', 'job__unical_id')
