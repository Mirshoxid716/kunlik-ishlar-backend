from django.apps import AppConfig
import threading

def create_default_admin():
    from django.contrib.auth.models import User
    from django.db.utils import OperationalError, ProgrammingError
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("Default admin created successfully on app start.")
    except (OperationalError, ProgrammingError, Exception) as e:
        print(f"Skipping admin creation (tables might not exist): {e}")

class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'

    def ready(self):
        import jobs.signals
        # Run in a separate thread to avoid AppRegistryNotReady exceptions during init
        threading.Thread(target=create_default_admin).start()
