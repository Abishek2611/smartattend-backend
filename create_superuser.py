import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from apps.accounts.models import User

email = os.environ.get('ADMIN_EMAIL')
password = os.environ.get('ADMIN_PASSWORD')
username = os.environ.get('ADMIN_USERNAME')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Admin',
        last_name='User',
        role='admin',
    )
    print("Superuser created!")
else:
    print("Already exists!")