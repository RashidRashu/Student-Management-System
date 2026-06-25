from django.contrib import admin
from .models import Student, Course, Enrollment, Attendance
from .models import Announcement


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'first_name', 'last_name', 'class_name')
    search_fields = ('first_name', 'last_name', 'roll_number')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'teacher_name')
    search_fields = ('course_code', 'course_name', 'teacher_name')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'marks', 'grade_letter')
    search_fields = ('student__roll_number', 'course__course_code', 'course__course_name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'course', 'student', 'status')
    list_filter = ('date', 'course', 'status')
    search_fields = ('student__roll_number', 'course__course_code', 'course__course_name')

admin.site.register(Announcement)