from django.core.exceptions import PermissionDenied

def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'STUDENT':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
