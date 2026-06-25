from django.apps import AppConfig
import re


class StudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'students'

    def ready(self):

        from django.contrib.auth.models import User, Group
        from .models import Course

        def teacher_username(name):
            slug = re.sub(r'[^\w\s]', '', name.lower().strip())
            return re.sub(r'\s+', '_', slug)

        instructor_group, _ = Group.objects.get_or_create(name="Instructor")

        for course in Course.objects.all():

            if not course.teacher_name:
                continue

            username = teacher_username(course.teacher_name)
            password = f"{username}@sms"

            user, _ = User.objects.get_or_create(username=username)

            user.set_password(password)

            parts = course.teacher_name.split()
            user.first_name = parts[0] if parts else ""
            user.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

            user.save()

            user.groups.add(instructor_group)

            if course.teacher_id != user.id:
                course.teacher = user
                course.save(update_fields=["teacher"])