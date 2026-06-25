from django.shortcuts import redirect
from functools import wraps


def admin_login_required(view_func):
    """
    Decorator for views that require admin/staff login.
    Redirects to the unified login page.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_login_required(view_func):
    """
    Decorator for views that require a student to be logged in.
    Redirects to the unified login page.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def instructor_login_required(view_func):
    """
    Decorator for views that require an Instructor login.
    The user must be authenticated AND belong to the 'Instructor' group.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.groups.filter(name='Instructor').exists():
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
