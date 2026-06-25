import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studentms.settings')
django.setup()

from django.contrib.auth.models import User, Group
from students.models import Course

print("=== COURSES ===")
for c in Course.objects.all():
    print(f"  {c.course_code} | teacher_name='{c.teacher_name}' | teacher={c.teacher}")
print(f"Total courses: {Course.objects.count()}")

print("\n=== INSTRUCTOR GROUP ===")
g = Group.objects.filter(name='Instructor').first()
print(f"Group 'Instructor' exists: {g is not None}")

print("\n=== INSTRUCTOR USERS ===")
if g:
    for u in User.objects.filter(groups=g):
        print(f"  username='{u.username}', has_usable_password={u.has_usable_password()}")
else:
    print("  (no group found)")

print("\n=== ALL USERS ===")
for u in User.objects.all():
    print(f"  username='{u.username}', is_staff={u.is_staff}, has_usable_password={u.has_usable_password()}, groups={list(u.groups.values_list('name', flat=True))}")
