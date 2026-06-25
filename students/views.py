from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Course, Enrollment, Attendance, Announcement
from .forms import StudentForm, EnrollmentForm, AnnouncementForm, CourseForm
from django.contrib import messages
from django.db.models import Avg
from datetime import date as dt_date
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import admin_login_required, student_login_required, instructor_login_required


# ─────────────────────────────────────────────
#  LANDING & ROOT
# ─────────────────────────────────────────────

def landing(request):
    """Root landing page — smart redirect if already logged in."""
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.groups.filter(name='Instructor').exists():
            return redirect('instructor_dashboard')
        else:
            return redirect('student_portal')
    return render(request, 'students/landing.html')


# ─────────────────────────────────────────────
#  ADMIN AUTH
# ─────────────────────────────────────────────

def login_view(request):
    """Unified login page for admin, instructor, and student accounts."""
    if request.user.is_authenticated:
        return redirect('landing')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, 'students/login.html', {
                'error': 'Invalid username or password.'
            })

        login(request, user)
        if user.is_staff or user.is_superuser:
            return redirect('admin_dashboard')
        if user.groups.filter(name='Instructor').exists():
            return redirect('instructor_dashboard')
        return redirect('student_portal')

    return render(request, 'students/login.html')


def admin_logout(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────
#  ADMIN DASHBOARD
# ─────────────────────────────────────────────

@admin_login_required
def admin_dashboard(request):
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    recent_announcements = Announcement.objects.filter(is_active=True).order_by('-date_posted')[:5]
    recent_students = Student.objects.order_by('-id')[:5]

    return render(request, 'students/home.html', {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'recent_announcements': recent_announcements,
        'recent_students': recent_students,
    })


# kept for backward-compat (home view redirects to dashboard)
def home(request):
    return redirect('admin_dashboard')


# ─────────────────────────────────────────────
#  STUDENTS — ADMIN VIEWS
# ─────────────────────────────────────────────

@admin_login_required
def student_list(request):
    query = request.GET.get('q')
    students = Student.objects.all()
    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(roll_number__icontains=query) |
            Q(class_name__icontains=query)
        )
    students = students.order_by('class_name', 'roll_number')
    return render(request, 'students/student_list.html', {
        'students': students,
        'query': query
    })


@admin_login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    average_marks = enrollments.aggregate(avg=Avg('marks'))['avg']

    overall_grade = None
    if average_marks is not None:
        if average_marks >= 90:
            overall_grade = 'A'
        elif average_marks >= 80:
            overall_grade = 'B'
        elif average_marks >= 70:
            overall_grade = 'C'
        elif average_marks >= 60:
            overall_grade = 'D'
        else:
            overall_grade = 'F'

    total_by_course = (
        Attendance.objects.filter(student=student)
        .values('course_id')
        .annotate(total=Count('id'))
    )
    present_by_course = (
        Attendance.objects.filter(student=student, status=Attendance.PRESENT)
        .values('course_id')
        .annotate(present=Count('id'))
    )

    total_map = {x['course_id']: x['total'] for x in total_by_course}
    present_map = {x['course_id']: x['present'] for x in present_by_course}
    course_ids = list(total_map.keys())
    courses = {c.id: c for c in Course.objects.filter(id__in=course_ids)}

    attendance_rows = []
    for course_id, total in total_map.items():
        present = present_map.get(course_id, 0)
        percent = round((present / total) * 100, 2) if total else 0
        attendance_rows.append({
            'course': courses.get(course_id),
            'present': present,
            'total': total,
            'percent': percent,
        })
    attendance_rows.sort(key=lambda r: (r['course'].course_code if r['course'] else ''))

    return render(request, 'students/student_detail.html', {
        'student': student,
        'enrollments': enrollments,
        'average_marks': average_marks,
        'overall_grade': overall_grade,
        'attendance_rows': attendance_rows,
    })


@admin_login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'students/student_form.html', {'form': form})


@admin_login_required
def edit_student(request, id):
    student = get_object_or_404(Student, id=id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect('student_detail', pk=student.id)
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {'form': form})


@admin_login_required
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})


# ─────────────────────────────────────────────
#  COURSES — ADMIN VIEWS
# ─────────────────────────────────────────────

@admin_login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'students/course_list.html', {'courses': courses})


@admin_login_required
def instructor_list(request):
    # Show all instructors and the courses they teach.
    courses = Course.objects.order_by('teacher_name', 'course_code')
    student_count = Student.objects.count()
    course_count = courses.count()
    recent_students = Student.objects.order_by('-id')[:6]
    top_courses = Course.objects.order_by('course_code')[:6]
    return render(request, 'students/instructor_list.html', {
        'courses': courses,
        'student_count': student_count,
        'course_count': course_count,
        'recent_students': recent_students,
        'top_courses': top_courses,
    })


@admin_login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course)
    return render(request, 'students/course_detail.html', {
        'course': course,
        'enrollments': enrollments
    })


@admin_login_required
def enroll_student(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            course = form.cleaned_data['course']
            if not Enrollment.objects.filter(student=student, course=course).exists():
                form.save()
            return redirect('student_detail', pk=student.id)
    else:
        form = EnrollmentForm()
    return render(request, 'students/enrollment_form.html', {'form': form})


# ─────────────────────────────────────────────
#  GRADES — ADMIN VIEWS
# ─────────────────────────────────────────────

@admin_login_required
def grade_entry(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course)
    return render(request, 'students/grade_entry.html', {
        'course': course,
        'enrollments': enrollments
    })


@admin_login_required
def enter_grades(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = (
        Enrollment.objects
        .filter(course=course)
        .select_related("student")
        .order_by("student__roll_number")
    )

    if request.method == "POST":
        for e in enrollments:
            marks_key = f"marks_{e.id}"
            marks_val = request.POST.get(marks_key)

            if marks_val is None or marks_val.strip() == "":
                e.marks = None
                e.grade_letter = None
                e.save(update_fields=["marks", "grade_letter"])
                continue

            try:
                marks = float(marks_val)
            except ValueError:
                continue

            marks = max(0, min(100, marks))
            e.marks = marks

            if marks >= 90:
                e.grade_letter = "A"
            elif marks >= 80:
                e.grade_letter = "B"
            elif marks >= 70:
                e.grade_letter = "C"
            elif marks >= 60:
                e.grade_letter = "D"
            else:
                e.grade_letter = "F"

            e.save(update_fields=["marks", "grade_letter"])

        messages.success(request, "Grades saved successfully.")
        return redirect("course_detail", course_id=course.id)

    return render(request, "students/enter_grades.html", {
        "course": course,
        "enrollments": enrollments
    })


# ─────────────────────────────────────────────
#  ATTENDANCE — ADMIN VIEWS
# ─────────────────────────────────────────────

@admin_login_required
def mark_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related("student")
    students = [e.student for e in enrollments]

    date_str = request.GET.get("date") or request.POST.get("date")
    selected_date = dt_date.fromisoformat(date_str) if date_str else dt_date.today()

    existing = Attendance.objects.filter(course=course, date=selected_date)
    existing_map = {a.student_id: a.status for a in existing}

    if request.method == "POST":
        present_ids = set(map(int, request.POST.getlist("present")))
        for s in students:
            status = Attendance.PRESENT if s.id in present_ids else Attendance.ABSENT
            Attendance.objects.update_or_create(
                student=s, course=course, date=selected_date,
                defaults={"status": status}
            )
        return redirect("attendance_report", course_id=course.id)

    return render(request, "students/mark_attendence.html", {
        "course": course,
        "students": students,
        "selected_date": selected_date,
        "existing_map": existing_map,
    })


@admin_login_required
def attendance_report(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related("student")
    students = [e.student for e in enrollments]
    att_qs = Attendance.objects.filter(course=course).select_related("student")
    total_classes = att_qs.values("date").distinct().count()

    summary = []
    for s in students:
        present_count = att_qs.filter(student=s, status=Attendance.PRESENT).count()
        percentage = (present_count / total_classes * 100) if total_classes else 0
        summary.append({
            "student": s,
            "present": present_count,
            "total": total_classes,
            "percentage": round(percentage, 2),
        })

    dates = list(att_qs.values_list("date", flat=True).distinct().order_by("date"))
    status_map = {f"{a.date.isoformat()}_{a.student_id}": a.status for a in att_qs}

    return render(request, "students/attendance_report.html", {
        "course": course,
        "students": students,
        "dates": dates,
        "status_map": status_map,
        "summary": summary,
        "total_classes": total_classes,
    })


# ─────────────────────────────────────────────
#  REPORT CARD — ADMIN VIEW
# ─────────────────────────────────────────────

@admin_login_required
def report_card(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    average_marks = enrollments.aggregate(avg=Avg('marks'))['avg']

    overall_grade = None
    if average_marks is not None:
        if average_marks >= 90:
            overall_grade = 'A'
        elif average_marks >= 80:
            overall_grade = 'B'
        elif average_marks >= 70:
            overall_grade = 'C'
        elif average_marks >= 60:
            overall_grade = 'D'
        else:
            overall_grade = 'F'

    report_data = []
    for enrollment in enrollments:
        total_classes = Attendance.objects.filter(student=student, course=enrollment.course).count()
        present_classes = Attendance.objects.filter(
            student=student, course=enrollment.course, status='Present'
        ).count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        report_data.append({
            'course': enrollment.course,
            'marks': enrollment.marks,
            'grade': enrollment.grade_letter,
            'attendance': round(attendance_percentage, 2)
        })

    return render(request, 'students/report_card.html', {
        'student': student,
        'report_data': report_data,
        'average_marks': average_marks,
        'overall_grade': overall_grade,
        'total_courses': enrollments.count()
    })


# ─────────────────────────────────────────────
#  ANNOUNCEMENTS — ADMIN CRUD
# ─────────────────────────────────────────────

@admin_login_required
def announcement_list(request):
    announcements = Announcement.objects.all().order_by('-date_posted')
    return render(request, 'students/announcement_list.html', {'announcements': announcements})


@admin_login_required
def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    return render(request, 'students/announcement_detail.html', {'announcement': announcement})


@admin_login_required
def add_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement posted successfully.")
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'students/announcement_form.html', {
        'form': form,
        'title': 'New Announcement'
    })


@admin_login_required
def edit_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated.")
            return redirect('announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'students/announcement_form.html', {
        'form': form,
        'title': 'Edit Announcement'
    })


@admin_login_required
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, "Announcement deleted.")
        return redirect('announcement_list')
    return render(request, 'students/announcement_confirm_delete.html', {
        'announcement': announcement
    })


# ─────────────────────────────────────────────
#  STUDENT AUTH
# ─────────────────────────────────────────────

def student_login(request):
    return login_view(request)


def student_logout(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────
#  STUDENT PORTAL
# ─────────────────────────────────────────────

@student_login_required
def student_portal(request):
    student = get_object_or_404(Student, user=request.user)
    enrollments = Enrollment.objects.filter(student=student).select_related("course")

    average_marks = enrollments.aggregate(avg=Avg("marks"))["avg"]
    overall_grade = None
    if average_marks is not None:
        if average_marks >= 90:   overall_grade = "A"
        elif average_marks >= 80: overall_grade = "B"
        elif average_marks >= 70: overall_grade = "C"
        elif average_marks >= 60: overall_grade = "D"
        else:                     overall_grade = "F"

    course_cards = []
    for e in enrollments:
        total = Attendance.objects.filter(student=student, course=e.course).count()
        present = Attendance.objects.filter(student=student, course=e.course, status="Present").count()
        percent = (present / total * 100) if total else 0
        course_cards.append({
            "course": e.course,
            "marks": e.marks,
            "grade": e.grade_letter,
            "attendance": round(percent, 2),
        })

    announcements = Announcement.objects.filter(is_active=True).order_by('-date_posted')[:5]

    return render(request, "students/student_portal.html", {
        "student": student,
        "courses": course_cards,
        "average_marks": average_marks,
        "overall_grade": overall_grade,
        "total_courses": enrollments.count(),
        "announcements": announcements,
    })


@student_login_required
def student_course_detail(request, course_id):
    student = get_object_or_404(Student, user=request.user)
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(student=student, course=course).select_related("course").first()

    if enrollment is None:
        return render(request, "students/student_course_detail.html", {"not_allowed": True})

    total = Attendance.objects.filter(student=student, course=course).count()
    present = Attendance.objects.filter(student=student, course=course, status="Present").count()
    percent = (present / total * 100) if total else 0

    return render(request, "students/student_course_detail.html", {
        "student": student,
        "course": course,
        "enrollment": enrollment,
        "total_classes": total,
        "present_classes": present,
        "attendance_percent": round(percent, 2),
    })


@student_login_required
def student_report_card(request):
    """Students can view their own report card."""
    student = get_object_or_404(Student, user=request.user)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    average_marks = enrollments.aggregate(avg=Avg('marks'))['avg']

    overall_grade = None
    if average_marks is not None:
        if average_marks >= 90:   overall_grade = 'A'
        elif average_marks >= 80: overall_grade = 'B'
        elif average_marks >= 70: overall_grade = 'C'
        elif average_marks >= 60: overall_grade = 'D'
        else:                     overall_grade = 'F'

    report_data = []
    for enrollment in enrollments:
        total_classes = Attendance.objects.filter(student=student, course=enrollment.course).count()
        present_classes = Attendance.objects.filter(
            student=student, course=enrollment.course, status='Present'
        ).count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        report_data.append({
            'course': enrollment.course,
            'marks': enrollment.marks,
            'grade': enrollment.grade_letter,
            'attendance': round(attendance_percentage, 2)
        })

    return render(request, 'students/student_report_card.html', {
        'student': student,
        'report_data': report_data,
        'average_marks': average_marks,
        'overall_grade': overall_grade,
        'total_courses': enrollments.count()
    })


def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()

    return render(request, 'students/add_course.html', {'form': form})


# ─────────────────────────────────────────────
#  INSTRUCTOR AUTH
# ─────────────────────────────────────────────

def instructor_login(request):
    return login_view(request)


def instructor_logout(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────
#  INSTRUCTOR DASHBOARD
# ─────────────────────────────────────────────

@instructor_login_required
def instructor_dashboard(request):
    """Shows all courses where course.teacher == request.user."""
    courses = Course.objects.filter(teacher=request.user)
    total_students = sum(
        Enrollment.objects.filter(course=c).count() for c in courses
    )
    announcements = Announcement.objects.filter(is_active=True).order_by('-date_posted')[:5]
    return render(request, 'students/instructor_dashboard.html', {
        'courses': courses,
        'total_courses': courses.count(),
        'total_students': total_students,
        'announcements': announcements,
    })


@instructor_login_required
def instructor_course_detail(request, course_id):
    """Instructor view of a specific course (must be their course)."""
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    return render(request, 'students/instructor_course_detail.html', {
        'course': course,
        'enrollments': enrollments,
    })


# ─────────────────────────────────────────────
#  INSTRUCTOR — ATTENDANCE
# ─────────────────────────────────────────────

@instructor_login_required
def instructor_mark_attendance(request, course_id):
    """Instructor marks attendance for their own course."""
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    students = [e.student for e in enrollments]

    date_str = request.GET.get('date') or request.POST.get('date')
    selected_date = dt_date.fromisoformat(date_str) if date_str else dt_date.today()

    existing = Attendance.objects.filter(course=course, date=selected_date)
    existing_map = {a.student_id: a.status for a in existing}

    if request.method == 'POST':
        present_ids = set(map(int, request.POST.getlist('present')))
        for s in students:
            status = Attendance.PRESENT if s.id in present_ids else Attendance.ABSENT
            Attendance.objects.update_or_create(
                student=s, course=course, date=selected_date,
                defaults={'status': status}
            )
        messages.success(request, 'Attendance saved successfully.')
        return redirect('instructor_attendance_report', course_id=course.id)

    return render(request, 'students/mark_attendence.html', {
        'course': course,
        'students': students,
        'selected_date': selected_date,
        'existing_map': existing_map,
        'back_url': 'instructor_course_detail',
        'is_instructor': True,
    })


@instructor_login_required
def instructor_attendance_report(request, course_id):
    """Attendance report for instructor's course."""
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    students = [e.student for e in enrollments]
    att_qs = Attendance.objects.filter(course=course).select_related('student')
    total_classes = att_qs.values('date').distinct().count()

    summary = []
    for s in students:
        present_count = att_qs.filter(student=s, status=Attendance.PRESENT).count()
        percentage = (present_count / total_classes * 100) if total_classes else 0
        summary.append({
            'student': s,
            'present': present_count,
            'total': total_classes,
            'percentage': round(percentage, 2),
        })

    dates = list(att_qs.values_list('date', flat=True).distinct().order_by('date'))
    status_map = {f"{a.date.isoformat()}_{a.student_id}": a.status for a in att_qs}

    return render(request, 'students/attendance_report.html', {
        'course': course,
        'students': students,
        'dates': dates,
        'status_map': status_map,
        'summary': summary,
        'total_classes': total_classes,
        'is_instructor': True,
    })


# ─────────────────────────────────────────────
#  INSTRUCTOR — GRADES
# ─────────────────────────────────────────────

@instructor_login_required
def instructor_enter_grades(request, course_id):
    """Instructor enters grades for their own course."""
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = (
        Enrollment.objects
        .filter(course=course)
        .select_related('student')
        .order_by('student__roll_number')
    )

    if request.method == 'POST':
        for e in enrollments:
            marks_key = f'marks_{e.id}'
            marks_val = request.POST.get(marks_key)

            if marks_val is None or marks_val.strip() == '':
                e.marks = None
                e.grade_letter = None
                e.save(update_fields=['marks', 'grade_letter'])
                continue

            try:
                marks = float(marks_val)
            except ValueError:
                continue

            marks = max(0, min(100, marks))
            e.marks = marks

            if marks >= 90:   e.grade_letter = 'A'
            elif marks >= 80: e.grade_letter = 'B'
            elif marks >= 70: e.grade_letter = 'C'
            elif marks >= 60: e.grade_letter = 'D'
            else:             e.grade_letter = 'F'

            e.save(update_fields=['marks', 'grade_letter'])

        messages.success(request, 'Grades saved successfully.')
        return redirect('instructor_course_detail', course_id=course.id)

    return render(request, 'students/enter_grades.html', {
        'course': course,
        'enrollments': enrollments,
        'is_instructor': True,
    })


# ─────────────────────────────────────────────
#  INSTRUCTOR — REPORT CARD
# ─────────────────────────────────────────────

@instructor_login_required
def instructor_report_card(request, pk):
    """Instructor can view a student's report card (for a student in their course)."""
    student = get_object_or_404(Student, pk=pk)
    # Verify at least one of the instructor's courses has this student enrolled
    instructor_courses = Course.objects.filter(teacher=request.user)
    if not Enrollment.objects.filter(student=student, course__in=instructor_courses).exists():
        messages.error(request, 'You can only view report cards for students in your courses.')
        return redirect('instructor_dashboard')

    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    average_marks = enrollments.aggregate(avg=Avg('marks'))['avg']

    overall_grade = None
    if average_marks is not None:
        if average_marks >= 90:   overall_grade = 'A'
        elif average_marks >= 80: overall_grade = 'B'
        elif average_marks >= 70: overall_grade = 'C'
        elif average_marks >= 60: overall_grade = 'D'
        else:                     overall_grade = 'F'

    report_data = []
    for enrollment in enrollments:
        total_classes = Attendance.objects.filter(student=student, course=enrollment.course).count()
        present_classes = Attendance.objects.filter(
            student=student, course=enrollment.course, status='Present'
        ).count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        report_data.append({
            'course': enrollment.course,
            'marks': enrollment.marks,
            'grade': enrollment.grade_letter,
            'attendance': round(attendance_percentage, 2)
        })

    return render(request, 'students/report_card.html', {
        'student': student,
        'report_data': report_data,
        'average_marks': average_marks,
        'overall_grade': overall_grade,
        'total_courses': enrollments.count(),
        'is_instructor': True,
    })

@instructor_login_required
def instructor_add_announcement(request):

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        Announcement.objects.create(
            title=title,
            content=content,
            instructor=request.user
        )

        return redirect("instructor_dashboard")

    return render(request, "students/instructor_add_announcement.html")

def startup_landing(request):
    return render(request, "students/startup_landing.html")