from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def unauthenticated_user(view_func):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view_func(request,*args,**kwargs)
    return wrapper_func

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def staff_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You don't have permission to access this page")
            return redirect('unauthorized')
    return wrapper_func

def admin_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='admin').exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Admin access required")
            return redirect('unauthorized')
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
