"""
Run this with:  py fix_instructors_direct.py
It directly fixes all instructor accounts without needing manage.py commands.
"""
import sys
import os
import django
import re

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studentms.settings')
django.setup()

from django.contrib.auth.models import User, Group
from students.models import Course


def teacher_username(name):
    slug = re.sub(r'[^\w\s]', '', name.lower().strip())
    return re.sub(r'\s+', '_', slug)


def main():
    instructor_group, _ = Group.objects.get_or_create(name='Instructor')
    courses = list(Course.objects.all())

    if not courses:
        print("No courses found in the database.")
        return

    print(f"Found {len(courses)} course(s). Processing...\n")

    for course in courses:
        if not course.teacher_name:
            print(f"  SKIP  {course.course_code} — no teacher_name")
            continue

        username = teacher_username(course.teacher_name)
        if not username:
            continue

        password = f"{username}@sms"

        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)   # Always set — fixes broken accounts
        parts = course.teacher_name.split()
        user.first_name = parts[0]
        user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        user.save()

        user.groups.add(instructor_group)

        # Link FK on course
        Course.objects.filter(pk=course.pk).update(teacher=user)

        action = "CREATED" if created else "FIXED "
        print(f"  [{action}]  username=\"{username}\"  password=\"{password}\"  course={course.course_code}")

    print("\n=== Done! ===")
    print("\nUse these credentials to log in at the Instructor login page:")
    print("  Username: <teacher name in lowercase with underscores>")
    print("  Password: <username>@sms")
    print("\nAll instructor accounts:")
    for u in User.objects.filter(groups=instructor_group):
        print(f"  - username=\"{u.username}\"  password=\"{u.username}@sms\"")


if __name__ == '__main__':
    main()
