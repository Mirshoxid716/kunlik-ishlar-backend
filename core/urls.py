from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def create_temp_admin(request):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        return HttpResponse("Admin created successfully! Username: admin, Password: admin")
    return HttpResponse("Admin already exists! Username: admin, Password: admin")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('setup-admin/', create_temp_admin),
    path('api/jobs/', include('jobs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
