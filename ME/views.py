from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

def back_up(request):
    return render(request, 'app1/admin_users_backup.html')

def base(request):
    return render(request, 'app1/base.html')

def user_settings_management(request):
    return render(request, 'app1/admin_users_settings.html')

def user_reports(request):
    return render(request, 'app1/admin_users_reports.html')

def user_form_management(request):
    return render(request, 'app1/admin_user_form_management.html')

def users_management(request): #
    return render(request, 'app1/admin_users_usermanagement.html')

def patients_management(request):
    return render(request, 'app1/admin_users_patients.html')

def users(request):
    return render(request, 'app1/admin_users_users.html')


