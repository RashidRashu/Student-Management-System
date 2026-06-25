from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
import re


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    roll_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    address = models.TextField()
    class_name = models.CharField(max_length=20)
    admission_date = models.DateField()

    def __str__(self):
        return f"{self.roll_number} - {self.first_name} {self.last_name}"


# ✅ SIGNAL MUST BE OUTSIDE THE CLASS
@receiver(post_save, sender=Student)
def create_student_user(sender, instance, created, **kwargs):
    if created and not instance.user:
        username = instance.roll_number
        password = f"{instance.roll_number}@123"

        user = User.objects.create_user(
            username=username,
            password=password,
            email=instance.email,
        )

        instance.user = user
        instance.save()

    
class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=100)
    description = models.TextField()
    teacher_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='courses_taught'
    )

    provider = models.CharField(max_length=120, default="Sociodynamics AI")

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

class Enrollment(models.Model):

    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]

    grade_letter = models.CharField(max_length=1, choices=GRADE_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.marks is not None:
            if self.marks >= 90:
                self.grade_letter = 'A'
            elif self.marks >= 80:
                self.grade_letter = 'B'
            elif self.marks >= 70:
                self.grade_letter = 'C'
            elif self.marks >= 60:
                self.grade_letter = 'D'
            else:
                self.grade_letter = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.course}"


class Attendance(models.Model):
    PRESENT = "Present"
    ABSENT = "Absent"

    STATUS_CHOICES = [
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT)

    class Meta:
        unique_together = ("student", "course", "date")
        ordering = ["-date", "student__roll_number"]

    def __str__(self):
        return f"{self.date} | {self.course.course_code} | {self.student.roll_number} | {self.status}"



class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_posted']

# ── Auto-create instructor login when a Course is saved ─────────────────────

def _teacher_username(teacher_name: str) -> str:
    """Convert 'John Smith' → 'john_smith'"""
    slug = re.sub(r'[^\w\s]', '', teacher_name.lower().strip())
    return re.sub(r'\s+', '_', slug)


@receiver(post_save, sender=Course)
def create_instructor_user(sender, instance, **kwargs):
    """
    Ensure a Django User exists for the teacher and link it to the course.
    Username format: teacher_name -> john_smith
    Password format: username@sms
    """

    if not instance.teacher_name:
        return

    username = _teacher_username(instance.teacher_name)

    if not username:
        return

    password = f"{username}@sms"

    # Create or get user
    user, created = User.objects.get_or_create(username=username)

    # ALWAYS ensure password matches rule
    user.set_password(password)

    name_parts = instance.teacher_name.split()

    user.first_name = name_parts[0] if name_parts else ''
    user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    user.save()

    # Add to Instructor group
    instructor_group, _ = Group.objects.get_or_create(name="Instructor")
    user.groups.add(instructor_group)

    # Link teacher to course safely
    if instance.teacher_id != user.id:
        Course.objects.filter(pk=instance.pk).update(teacher=user)