from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Student

@receiver(post_save, sender=Student)
def create_student_user(sender, instance, created, **kwargs):
    if created and instance.user is None:
        # username = roll number (simple)
        username = instance.roll_number
        password = f"{instance.roll_number}@123"  # change later

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
        )
        instance.user = user
        instance.save()