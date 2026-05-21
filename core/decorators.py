from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    return role_required('admin')(view_func)


def trainer_required(view_func):
    return role_required('admin', 'trainer')(view_func)


def athlete_required(view_func):
    return role_required('admin', 'trainer', 'athlete')(view_func)
