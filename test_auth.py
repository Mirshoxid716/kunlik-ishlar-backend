import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

user, created = User.objects.get_or_create(username='admin')
user.set_password('admin')
user.is_staff = True
user.is_superuser = True
user.save()

print(f"User 'admin' {'created' if created else 'updated'}.")
auth_user = authenticate(username='admin', password='admin')
print(f"Authentication with 'admin'/'admin': {'SUCCESS' if auth_user else 'FAILED'}")
