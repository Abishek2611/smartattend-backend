import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from apps.accounts.models import User, Department
from apps.leaves.models import LeaveType

# Admin create
email = os.environ.get('ADMIN_EMAIL')
password = os.environ.get('ADMIN_PASSWORD')
username = os.environ.get('ADMIN_USERNAME')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        username=username, email=email, password=password,
        first_name='Admin', last_name='User', role='admin',
    )
    print("Superuser created!")
else:
    print("Admin already exists!")

# Departments create
departments = ['Engineering', 'HR', 'Finance', 'Marketing']
for dept in departments:
    Department.objects.get_or_create(name=dept)
print("Departments created!")

# Leave Types create
leave_types = [
    {'name': 'Casual Leave', 'max_days': 12},
    {'name': 'Sick Leave', 'max_days': 15},
    {'name': 'Annual Leave', 'max_days': 21},
]
for lt in leave_types:
    LeaveType.objects.get_or_create(name=lt['name'], defaults={'max_days': lt['max_days']})
print("Leave types created!")