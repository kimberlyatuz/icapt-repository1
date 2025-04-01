from django.http import HttpResponse
from functools import wraps
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Redirect authenticated users based on their group
            if request.user.groups.filter(name='admin').exists():
                return redirect('/admin/')
            return redirect('index')  # Or your staff dashboard URL
        return view_func(request, *args, **kwargs)
    return wrapper_func

# role based permission and authentication
def allowed_users(allowed_roles = []):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('You are not authorised to view this page')
        return wrapper_func
    return decorator

def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name

        if group == 'staff':
            return redirect('ME_Dashboard')

        if group == 'admin':
            return view_func(request, *args, **kwargs)

        return HttpResponse('You are not authorized to view this page')  # Add a response for unauthorized access

    return wrapper_function
