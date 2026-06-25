import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from students.models import Course


def _teacher_username(teacher_name: str) -> str:
    """Convert 'John Smith' -> 'john_smith'"""
    slug = re.sub(r'[^\w\s]', '', teacher_name.lower().strip())
    return re.sub(r'\s+', '_', slug)


class Command(BaseCommand):
    help = 'Create/fix instructor user accounts for all existing courses'

    def handle(self, *args, **options):
        instructor_group, _ = Group.objects.get_or_create(name='Instructor')
        courses = Course.objects.all()

        if not courses.exists():
            self.stdout.write(self.style.WARNING('No courses found in the database.'))
            return

        for course in courses:
            if not course.teacher_name:
                self.stdout.write(f'  Skipping {course.course_code}: no teacher_name set')
                continue

            username = _teacher_username(course.teacher_name)
            if not username:
                continue

            password = f"{username}@sms"
            user, created = User.objects.get_or_create(username=username)

            # Always set password — fixes users created without one
            user.set_password(password)
            user.first_name = course.teacher_name.split()[0]
            user.last_name = ' '.join(course.teacher_name.split()[1:]) if len(course.teacher_name.split()) > 1 else ''
            user.save()

            # Add to Instructor group
            user.groups.add(instructor_group)

            # Link course.teacher FK
            Course.objects.filter(pk=course.pk).update(teacher=user)

            action = "Created" if created else "Fixed"
            self.stdout.write(self.style.SUCCESS(
                f'  [{action}] username="{username}"  password="{password}"  course={course.course_code}'
            ))

        self.stdout.write(self.style.SUCCESS('\nDone! All instructor accounts are ready.'))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('  Username : <teacher name in lowercase with underscores, e.g. john_smith>')
        self.stdout.write('  Password : <username>@sms  (e.g. john_smith@sms)')
