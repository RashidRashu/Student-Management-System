from django.urls import path
from . import views

urlpatterns = [

    # ── ROOT / LANDING ──────────────────────────────────────────────────
    path('', views.startup_landing, name='startup'),
    path('app/', views.landing, name='landing'),

    # ── AUTH ─────────────────────────────────────────────────────────────
    path('login/', views.login_view, name='login'),
    path('admin/login/', views.login_view, name='admin_login'),
    path('student/login/', views.login_view, name='student_login'),
    path('instructor/login/', views.login_view, name='instructor_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('student/logout/', views.student_logout, name='student_logout'),
    path('instructor/logout/', views.instructor_logout, name='instructor_logout'),

    # ── ADMIN DASHBOARD ─────────────────────────────────────────────────
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ── STUDENTS (admin) ────────────────────────────────────────────────
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/edit/<int:id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:id>/', views.delete_student, name='delete_student'),
    path('students/<int:pk>/report/', views.report_card, name='report_card'),
    path('instructors/', views.instructor_list, name='instructor_list'),

    # ── COURSES (admin) ─────────────────────────────────────────────────
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/', views.enroll_student, name='enroll'),
    path('add-course/', views.add_course, name='add_course'),

    # ── GRADES (admin) ──────────────────────────────────────────────────
    path('course/<int:course_id>/grades/', views.grade_entry, name='grade_entry'),
    path('courses/<int:course_id>/grades/', views.enter_grades, name='enter_grades'),

    # ── ATTENDANCE (admin) ──────────────────────────────────────────────
    path('courses/<int:course_id>/attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('courses/<int:course_id>/attendance/report/', views.attendance_report, name='attendance_report'),

    # ── ANNOUNCEMENTS (admin CRUD) ──────────────────────────────────────
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/add/', views.add_announcement, name='add_announcement'),
    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/<int:pk>/edit/', views.edit_announcement, name='edit_announcement'),
    path('announcements/<int:pk>/delete/', views.delete_announcement, name='delete_announcement'),

    # ── STUDENT PORTAL ──────────────────────────────────────────────────
    path('student/portal/', views.student_portal, name='student_portal'),
    path('student/course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('student/report-card/', views.student_report_card, name='student_report_card'),

    # ── INSTRUCTOR DASHBOARD ─────────────────────────────────────────────
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),

    # ── INSTRUCTOR COURSES ───────────────────────────────────────────────
    path('instructor/course/<int:course_id>/', views.instructor_course_detail, name='instructor_course_detail'),

    # ── INSTRUCTOR ATTENDANCE ────────────────────────────────────────────
    path('instructor/course/<int:course_id>/attendance/mark/', views.instructor_mark_attendance, name='instructor_mark_attendance'),
    path('instructor/course/<int:course_id>/attendance/report/', views.instructor_attendance_report, name='instructor_attendance_report'),

    # ── INSTRUCTOR GRADES ────────────────────────────────────────────────
    path('instructor/course/<int:course_id>/grades/', views.instructor_enter_grades, name='instructor_enter_grades'),

    # ── INSTRUCTOR REPORT CARD ───────────────────────────────────────────
    path('instructor/student/<int:pk>/report-card/', views.instructor_report_card, name='instructor_report_card'),

    # ── INSTRUCTOR ANNOUNCEMENTS ───────────────────────────────────────
    path(
    'instructor/announcement/add/', views.instructor_add_announcement, name='instructor_add_announcement'),
]
