# for logging in and registering
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse
# for editing entered data after submissions
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import request, JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django import forms

from .decorators import unauthenticated_user, allowed_users, admin_only
from .models import UserForm, UserFormField, FormSubmission, UserProfile, PatientDemographics

from .forms import UserFormCreationForm, UserFormFieldCreationForm, CreateUserForm, ImportForm

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

#to help with debuging
import logging
logger = logging.getLogger(__name__)

from django.core.mail import send_mail
from django.conf import settings

# for exporting forms
from .resource import FormSubmissionResource
import pandas as pd #it makes exporting to xcel straightforwad
import csv
from django.http import HttpResponse
from openpyxl import Workbook
from io import BytesIO #openpyxl library Workbook.save() method does not return the workbook data directly so it is first saved in bytes10 then we return that to get the excel
from tablib import Dataset

#allow filters
from django.db.models import Q

#for linechart
from django.db.models import Count
# for line chart
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncMonth, TruncYear

# views.py  to dynamically generate the signed URL for the dashboard
import jwt
import time

#for the designing of forms using crispy forms bootstrap 5
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Field
from django import forms
#for importing forms that may have different date types
from django.core.management.base import BaseCommand
from dateutil import parser

#for audit trails
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST


logger = logging.getLogger(__name__)
# Create your views here.
def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # check if user is admin or staff
            if user.groups.filter(name='admin').exists():
                return redirect('admin:index')  # direct to the dashboard
            else:
                return redirect('index')  # direct to the homepage
        else:
            messages.info(request, 'Username/Password is incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)

def logoutuser(request):
    logout(request)
    return redirect('login')

@unauthenticated_user
def register(request):
    #add the built in django form for registration
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='staff')
            user.groups.add(group)

            messages.success(request,'Account was created for ' + username)
            return redirect('login')

    context = {'form':form}
    return render(request, 'accounts/register.html', context)

def unauthorized(request):
    return HttpResponseForbidden("You don't have access to this page.")


@login_required(login_url='login')
def index(request):
    # Check group membership more gracefully
    if not request.user.groups.filter(name='staff').exists():
        # Redirect to appropriate page or show unauthorized message
        return redirect('unauthorized')
    # Get all submissions (or adjust query as needed)
    submissions = FormSubmission.objects.all()

    # Get staff group members
    staff_group = get_object_or_404(Group, name='staff')
    staff_users = staff_group.user_set.all()

    # Get rejected submissions for staff group members
    rejected_submissions = FormSubmission.objects.filter(
        user__in=staff_users,
        status='rejected'
    )

    context = {
        'submissions': submissions,
        'rejected_submissions': rejected_submissions,
    }

    return render(request, 'app1/home.html', context)

@login_required(login_url='login')
def add_user(request):
    return render(request, 'app1/admin_add_user.html')

@login_required(login_url='login')
def enter_data(request):
    return render(request, 'app1/enter_data.html')

@login_required(login_url='login')
def predictive_analytics(request):
    return render(request, 'app1/predictive_analytics.html')

def reset_password(request):
    return render(request, 'app1/reset_password.html')

def forgot_password(request):
    return render(request, 'app1/forgot_password.html')

@login_required(login_url='login')
def ReviewRecords(request, submission_id):
    try:
        submission = get_object_or_404(FormSubmission, id=submission_id)
        return render(request, 'app1/ReviewRecords.html', {'submission': submission})  # Pass as singular
    except FormSubmission.DoesNotExist:
        return HttpResponse("No valid submission ID found!")

@login_required(login_url='login')
def Forms(request):
    query = request.GET.get('q')  # Getting the search query
    if query:
        user_forms = UserForm.objects.filter(title__icontains=query)  # Adjust the field as needed
    else:
        user_forms = UserForm.objects.all()
    return render(request, 'app1/forms.html', {'user_forms': user_forms})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
# to allow users to make their own forms
def create_user_form(request):
    if request.method == 'POST':
        form = UserFormCreationForm(request.POST or None)
        if form.is_valid():
            user_form = form.save(commit=False)
            user_form.creator = request.user  # Set the creator to the current user
            user_form.save()

            # Process fields
            field_labels = request.POST.getlist('field_label')
            field_types = request.POST.getlist('field_type')
            field_required = request.POST.getlist('field_required')
            field_options = request.POST.getlist('field_options')
            field_placeholders = request.POST.getlist('field_placeholder')

            for i in range(len(field_labels)):
                UserFormField.objects.create(
                    user_form=user_form,
                    label=field_labels[i],
                    field_type=field_types[i],
                    placeholder=field_placeholders[i],
                    # it was causing problems when i want to create form (..out of index)  required=field_required[i] == 'on',
                    position=i
                )

            return redirect('user_forms_list')
    else:
        form = UserFormCreationForm()

    return render(request, 'app1/create_forms.html', {'form': form})


# View to create a new field for a specific UserForm
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def create_user_form_field(request, form_id):
    if request.method == 'POST':
        field_labels = request.POST.getlist('field_label')
        field_types = request.POST.getlist('field_type')
        field_required = request.POST.getlist('field_required')
        field_placeholders = request.POST.getlist('field_placeholder')

        user_form = UserForm.objects.create(
            creator=request.user,
            title=request.POST['title'],
            description=request.POST.get('description', '')
        )
        return redirect('user_forms_list')

        # Make sure all list lengths match
        if (len(field_labels) == len(field_types) == len(field_required) == len(field_placeholders)):
            for i in range(len(field_labels)):
                UserFormField.objects.create(
                    user_form=user_form,
                    label=field_labels[i],
                    field_type=field_types[i],
                    required=(field_required[i] == 'on'),
                    placeholder=field_placeholders[i],
                    position=i
                )
                return redirect('user_forms_list')
            else:
                # Handle the case where list lengths do not match
                messages.error(request, 'Field labels, types, and requirements must match in length.')
                return redirect('form_creation_page')

        else:
            form = UserFormCreationForm()
        return render(request, 'form_template.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def edit_user_form(request, form_id):
    user_form = get_object_or_404(UserForm, id=form_id)

    if request.method == 'POST':
        # Update user form details
        user_form.title = request.POST.get('title')
        user_form.description = request.POST.get('description')
        messages.success(request, "Form updated successfully!")
        if request.user.is_authenticated:
            user_form.creator = request.user  # Ensure creator is set
        else:
            print("Error: Attempt to save a form without an authenticated user.")
            return redirect('login')

        print(f"Setting creator to: {user_form.creator}")  # Debugging output
        user_form.save()

        # Process existing and new fields
        field_ids = request.POST.getlist('field_ids')  # Get existing field IDs
        new_labels = request.POST.getlist('field_labels')  # Get new/edited field labels
        new_types = request.POST.getlist('field_types')
        # new_types = [request.POST.get(f'field_types_{field_id}') for field_id in field_ids]  # Match field_ids

        # Handle deletions
        if 'delete_field' in request.POST:
            field_id = request.POST['delete_field']
            field_to_delete = get_object_or_404(UserFormField, id=field_id)
            field_to_delete.delete()
            # Redirect to the same edit user form to refresh the context
            return redirect('edit_user_form', form_id=form_id)

        # Update existing fields
        for idx, field_id in enumerate(field_ids):
                field = get_object_or_404(UserFormField, id=field_id)
                field.label = new_labels[idx]
                field.field_type = new_types[idx]
                # field.field_type = request.POST.get(f'field_types_{field_id}', '')  # Use .get to prevent KeyError
                field.save()

        # Handle new fields
        for i in range(len(field_ids), len(new_labels)):
            if i < len(new_labels) and i < len(new_types):  # Ensure both lists have the required length
                new_field = UserFormField(user_form=user_form, label=new_labels[i], field_type=new_types[i], required=True, user=request.user)
                try:
                 new_field.save()  # Attempt to save the new field
                except Exception as e:
                    print(f"Error saving new field: {e}")  # Debugging output to understand the issue

        return redirect('edit_user_form', form_id=user_form.id)  # Redirect to display the updated form

    # If it's a GET request, render the form with the current user_form data
    return render(request, 'app1/edit_user_form.html', {
        'user_form': user_form,
        'fields': UserFormField.objects.filter(user_form=user_form),
        'first_field_label': user_form.title
    })

@login_required(login_url='login')
def view_user_form(request, form_id):
    user_form = get_object_or_404(UserForm, id=form_id)
    fields = user_form.fields.all()  # Get all fields associated with this form

    return render(request, 'app1/view_user_form.html', {
        'user_form': user_form,
        'fields': fields,
    })


# View to list all UserForms created by the user (optional)
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff', 'admin'])
def user_forms_list(request):
    user_forms = UserForm.objects.all()

    # Check if the user is in the 'staff' group
    is_staff = request.user.groups.filter(name='staff').exists()

    return render(request, 'app1/user_forms_list.html', {
        'user_forms': user_forms,
        'is_staff': is_staff,  # Pass the staff check to the template
    })

# View to list all fields for a specific UserForm
@login_required(login_url='login')
def form_fields_list(request, form_id):
    user_form = get_object_or_404(UserForm, id=form_id)
    fields = user_form.fields.all()

    if request.method == 'POST':
        # Ensure to save your form data if applicable
        user_form.save()
        # Redirect or render a success message here
        return redirect('form_submission_success')

    # Render the view only if it's a GET request
    return render(request, 'app1/form_fields_list.html', {
        'user_form': user_form,
        'fields': fields})

@login_required(login_url='login')
def form_view(request, form_id):
    user_form_instance = get_object_or_404(UserForm, id=form_id)
    fields = user_form_instance.fields.all()  # Get associated fields
    user = request.user  # This assumes the user is logged in

    # Create a dynamic form class
    class DynamicUserForm(forms.Form):
        pass

    for field in fields:
        field_type = field.field_type
        if field_type == 'text':
            DynamicUserForm.base_fields[field.label] = forms.CharField(
                required=field.required,
                label=field.label,
                widget=forms.TextInput(attrs={'placeholder': field.placeholder})
            )
        elif field_type == 'textarea':
            DynamicUserForm.base_fields[field.label] = forms.CharField(
                required=field.required,
                label=field.label,
                widget=forms.Textarea(attrs={'placeholder': field.placeholder})
            )
        elif field_type == 'select':
            choices = [(option, option) for option in field.get_options()]
            DynamicUserForm.base_fields[field.label] = forms.ChoiceField(
                required=field.required,
                label=field.label,
                choices=choices,
                widget=forms.Select(attrs={'placeholder': field.placeholder})
            )
        elif field_type == 'checkbox':
            DynamicUserForm.base_fields[field.label] = forms.BooleanField(
                required=field.required,
                label=field.label
            )
        elif field_type == 'radio':
            choices = [(option, option) for option in field.get_options()]
            DynamicUserForm.base_fields[field.label] = forms.ChoiceField(
                required=field.required,
                label=field.label,
                widget=forms.RadioSelect,
                choices=choices
            )
        elif field_type == 'email':
            DynamicUserForm.base_fields[field.label] = forms.EmailField(
                required=field.required,
                label=field.label,
                widget=forms.EmailInput(attrs={'placeholder': field.placeholder})
            )
        elif field_type == 'number':
            DynamicUserForm.base_fields[field.label] = forms.IntegerField(
                required=field.required,
                label=field.label,
                widget=forms.NumberInput(attrs={'placeholder': field.placeholder})
            )
        elif field_type == 'date':
            DynamicUserForm.base_fields[field.label] = forms.DateField(
                required=field.required,
                label=field.label,
                widget=forms.DateInput(attrs={'type': 'date', 'placeholder': field.placeholder})
            )

    if request.method == 'POST':
        form = DynamicUserForm(request.POST)
        if form.is_valid():
            # Check for required fields
            for field in fields:
                if field.required and not form.cleaned_data.get(field.label):
                    messages.error(request, f"{field.label} is required.")
                    return render(request, 'app1/form_view.html',
                                  {'form': form, 'user_form_instance': user_form_instance})

            # Handle the valid form data as needed
            data = {field.label: form.cleaned_data[field.label] for field in fields}

            # Convert date objects to string
            for key, value in data.items():
                if isinstance(value, date):
                    data[key] = value.isoformat()  # Convert to string

            # Create the FormSubmission instance with the user
            FormSubmission.objects.create(user=user, user_form=user_form_instance, data=data)

            return redirect('form_view', form_id=user_form_instance.id)
    else:
        form = DynamicUserForm()  # Initialize the form for GET requests

        # Set up the Crispy Forms helper
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Submit'))

    return render(request, 'app1/form_view.html', {
        'form': form,
        'user_form_instance': user_form_instance,
    })


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_user_form(request, form_id):
    form = get_object_or_404(UserForm, id=form_id)
    form.delete()
    return redirect('user_forms_list')  # Redirect to the list view after deletion

@login_required(login_url='login')
def fill_form(request, form_id):
    form_instance = UserForm.objects.get(id=form_id)
    if request.method == 'POST':
        logger.debug(f"Raw POST data: {request.POST}")  # Log the entire POST data
        # Collect the submitted data
        data = {field: request.POST[field] for field in request.POST}


        # Iterate through the fields of the form instance
        for field in form_instance.fields.all():
            # Get the value from the POST data for each field label
            data[field.label] = request.POST.get(field.label, '')  # Use an empty string as default if not found

        logger.debug(f"Parsed data: {data}")  # Log the parsed data

        # Create a FormSubmission instance
        FormSubmission.objects.create(user_form=form_instance, data=data)
        messages.success(request, "Your form has been submitted!")
        return redirect('form_submissions_success')

    return render(request, 'app1/form_view.html', {'form_instance': form_instance})

@login_required(login_url='login')
def list_form_submissions(request):
    submissions = FormSubmission.objects.all().order_by('-submitted_at')  # Retrieve all submissions
    return render(request, 'app1/form_submission_list.html', {'submissions': submissions})
    # return render(request, 'app1/submissions_overview.html', {'submissions': submissions})

@login_required(login_url='login')
def form_submission_success(request):
    return render(request, 'app1/form_submission_success.html')

# for admin to review the submissions from user
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def review_submissions(request, user_id):
    #submissions = FormSubmission.objects.filter(status='pending').order_by('user')
    user = get_object_or_404(User, id=user_id)
    # submissions = FormSubmission.objects.filter(user=user)
    submissions = FormSubmission.objects.all()

    # Handle filtering based on search query and statuses
    query = request.GET.get('q', '')
    status_filter = request.GET.getlist('status')  # Allows multiple statuses
    user_filter = request.GET.getlist('users')  # Allows multiple users if needed

    if query:
        submissions = submissions.filter(
            Q(user_form__title__icontains=query) |
            Q(feedback__icontains=query)
        )

    if status_filter:
        submissions = submissions.filter(status__in=status_filter)

    # Group submissions by user_form
    grouped_by_form = {}
    for sub in submissions:
        form = sub.user_form  # This points to the UserForm instance
        form_title = form.title if hasattr(form, 'title') else str(form)
        if form_title not in grouped_by_form:
            grouped_by_form[form_title] = []
        grouped_by_form[form_title].append(sub)


    if request.method == 'POST':
        for submission in submissions:
            submission.status = request.POST.get(f'status_{submission.id}', submission.status)
            submission.feedback = request.POST.get(f'feedback_{submission.id}', submission.feedback)
            submission.save()
        return redirect('review_user_submissions', user_id=user.id)


    return render(request, 'app1/review_submissions.html', {
        'user': user, 'grouped_by_form': grouped_by_form,'query': query, 'status_filter': status_filter,
    })
#  to fetch all users and their submissions
def submissions_list(request):
    # Fetch the "staff" group
    staff_group = Group.objects.get(name='staff')

    # Fetch all users that belong to the "staff" group
    staff_users = User.objects.filter(groups=staff_group)

    context = {
        'staff_users': staff_users,
    }
    return render(request, 'app1/submissions_list.html', context)

def user_submissions(request, user_id):
    # Fetch submissions for a specific user
    user = get_object_or_404(User, id=user_id)
    submissions = FormSubmission.objects.filter(user=user)

    # Handle bulk status update
    if request.method == 'POST' and 'action' in request.POST:
        if request.POST['action'] == 'update_all':
            new_status = request.POST.get('new_status')
            if new_status in ['pending', 'accepted', 'rejected']:
                submissions.update(status=new_status)
            return HttpResponseRedirect(reverse('user_submissions', args=[user_id]))


    # Extract field names from the JSON data of the first submission (if it exists)
    if submissions.exists():
        first_submission = submissions.first()
        field_names = list(first_submission.data.keys())  # Extract keys from the JSON data
    else:
        field_names = []  # No submissions, so no field names

        # Handle filtering based on status query parameter
        status_filter = request.GET.get('status')
        if status_filter in ['accepted', 'rejected']:
            submissions = submissions.filter(status=status_filter)

    context = {
        'user': user,
        'submissions': submissions,
        'field_names': field_names,  # Pass field names to the template
        'can_edit': request.user.is_staff,  # Allow editing if the user is staff
    }
    return render(request, 'app1/ user_submissions.html', context)

@csrf_exempt
def update_submission_status(request, submission_id):

    if request.method == 'POST':
        submission = get_object_or_404(FormSubmission, id=submission_id)
        status = request.POST.get('status')
        feedback = request.POST.get('feedback', '')  # Optional feedback for rejection
        submission.status = status
        submission.feedback = feedback
        submission.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
def update_submission(request, submission_id):
    submission = get_object_or_404(FormSubmission, id=submission_id)

    if request.method != 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)

            # Update the submission data
            submission_data = json.loads(submission.data)  # Ensure data is a dictionary
            for field_name, value in data.items():
                submission_data[field_name] = value  # Update individual fields

            # Save the updated data back to the submission
            submission.data = json.dumps(submission_data)
            submission.save()

            # Return a success response
            return JsonResponse({'success': True,
                                 'message': 'Updated successfully',
                                 })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# to send email to user when submission is rejected
@login_required(login_url='login')
def send_rejection_email(user_email, submission_data, feedback):
    subject = 'Your Submission Has Been Rejected'
    message = f"""
    Good day

Please review the errors in your submission.

    Submission Data:
    {submission_data}

    Feedback:
    {feedback}

    Thank you for your understanding.

    Best regards,
    Your Team
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )

@login_required(login_url='login')
def submissions(request):
    forms = UserForm.objects.all()  # Fetch all forms
    submissions = FormSubmission.objects.all()  # Default to all submissions
    field_names = []  # Initialize field names list
    can_edit = True  # Flag to determine if editing is allowed

    # If the user is not an admin, filter submissions to only their own
    if not request.user.is_superuser:
        submissions = submissions.filter(user=request.user)

    # Handle form selection for admins
    if request.user.is_superuser and request.method == 'POST' and 'form_id' in request.POST:
        form_id = request.POST.get('form_id')
        if form_id:
            submissions = submissions.filter(user_form_id=form_id)
            field_names = UserFormField.objects.filter(user_form_id=form_id).values_list('label', flat=True)

    # Handle actions (sync, edit, delete, export)
    if request.method == 'POST':
        if 'sync' in request.POST:
            submissions.update(synced=True)  # Update sync status for all filtered submissions
            return redirect('Submissions')

        if 'edit' in request.POST:
            submission_id = request.POST.get('submission_id')
            return redirect('edit_submission', submission_id=submission_id)

        if 'delete' in request.POST:
            submission_id = request.POST.get('submission_id')
            submission_to_delete = get_object_or_404(FormSubmission, id=submission_id)
            submission_to_delete.delete()
            messages.success(request, "Submission deleted successfully!")  # Add a success message
            return redirect('Submissions')

        if 'export_data' in request.POST:
            return export_data(request)

    # Fetch field names if not already fetched (for non-admin users)
    if not field_names and submissions.exists():
        form_id = submissions.first().user_form_id
        field_names = UserFormField.objects.filter(user_form_id=form_id).values_list('label', flat=True)

    return render(request, 'app1/submit.html', {
        'forms': forms,
        'submissions': submissions,
        'field_names': field_names,
        'can_edit': can_edit,
    })

@login_required(login_url='login')
def edit_submission(request, submission_id):
    submission = get_object_or_404(FormSubmission, id=submission_id)

    if request.method == 'POST':
        # Update the data dictionary with new values from the form
        new_data = {field.label: request.POST.get(field.label, '') for field in submission.user_form.fields.all()}
        submission.data = new_data  # Assuming data is a dictionary
        submission.save()
        messages.success(request, "Submission updated successfully!")
        return redirect('Submissions')

    # Check if the user is in the 'staff' group
    is_staff = request.user.groups.filter(name='staff').exists()

    return render(request, 'app1/edit_submission.html', {
        'submission': submission,
        'is_staff': is_staff,  # Pass the staff check to the template
    })


@login_required
@require_POST
def update_submission(request, submission_id):
    try:
        submission = FormSubmission.objects.get(id=submission_id)

        if not submission.is_editable():
            return JsonResponse({
                'success': False,
                'error': 'This submission can no longer be edited as it has been processed'
            }, status=403)

        if not (request.user == submission.user or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': "You don't have permission to edit this submission"
            }, status=403)

        try:
            update_data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON data: {str(e)}'
            }, status=400)

        current_data = submission.get_data()
        updated_fields = []

        for field_name, new_value in update_data.items():
            if field_name in current_data:
                current_data[field_name] = new_value
                updated_fields.append(field_name)

        submission.data = current_data

        try:
            submission.save()
            return JsonResponse({
                'success': True,
                'message': f'Updated {len(updated_fields)} field(s)',
                'updated_fields': updated_fields
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Database error: {str(e)}'
            }, status=500)

    except FormSubmission.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Submission not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)

    except FormSubmission.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Submission not found'}, status=404)
    except PermissionDenied as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


#exports
@login_required(login_url='login')
def export_data(request):
    if request.method == 'POST':
        # Get selected option from form
        selected_ids = request.POST.getlist('selected_items')
        file_format = request.POST.get('file-format')

        if not selected_ids:
            return HttpResponse("No items selected for export.", status=400)

        if file_format not in ['CSV', 'JSON', 'XLS (Excel)']:
            return HttpResponse("Invalid file format selected.", status=400)

        # Fetch the selected submissions
        submissions = FormSubmission.objects.filter(id__in=selected_ids)

        # Export the data
        forms_resource = FormSubmissionResource()
        dataset = forms_resource.export(submissions)

        if file_format == 'CSV':
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'
            return response
        elif file_format == 'JSON':
            response = HttpResponse(dataset.json, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="exported_data.json"'
            return response
        elif file_format == 'XLS (Excel)':
            response = HttpResponse(dataset.xlsx, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="exported_data.xls"'
            return response

    return render(request, 'app1/export.html', {'submissions': FormSubmission.objects.all()})

@login_required(login_url='login')
def import_data(request):
    user_forms = UserForm.objects.all()  # Fetch all UserForm instances

    if request.method == 'POST':
        file_format = request.POST['file-format']
        user_form_id = request.POST['user-form']
        new_forms = request.FILES['importData']

        try:
            # Fetch the selected form and its fields
            selected_form = UserForm.objects.get(id=user_form_id)
            form_fields = selected_form.fields.all()  # Fetch all fields of the selected form

            # Load the uploaded file into a dataset
            dataset = Dataset()
            if file_format == 'CSV':
                imported_data = dataset.load(new_forms.read().decode('utf-8'), format='csv')
            elif file_format == 'XLSX':
                imported_data = dataset.load(new_forms.read(), format='xlsx')
            elif file_format == 'JSON':
                imported_data = dataset.load(new_forms.read().decode('utf-8'), format='json')
            else:
                return render(request, 'app1/import.html', {'error': 'Unsupported file format', 'user_forms': user_forms})

            # Debugging: Print imported data
            print("Imported Data:", imported_data.dict)

            # Validate the imported data
            for row in imported_data.dict:
                # Check if all required fields are present in the row
                for field in form_fields:
                    if field.label not in row:
                        return render(request, 'app1/import.html', {'error': f'Missing field: {field.label}', 'user_forms': user_forms})

            # Save the imported data
            for row in imported_data.dict:
                # Create a dictionary to store the field values
                data_dict = {field.label: row[field.label] for field in form_fields}

                # Convert datetime objects to string
                for key, value in data_dict.items():
                    if isinstance(value, datetime):
                        data_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime as string

                # Validate data fields before importing
                for field in form_fields:
                    if field.label not in row:
                        return render(request, 'app1/import.html',
                                      {'error': f'Missing field: {field.label}', 'user_forms': user_forms})

                    # Example: Validate that 'age' is a number
                    if field.label == 'age' and not row[field.label].isdigit():
                        return render(request, 'app1/import.html',
                                      {'error': f'Invalid data type for field: {field.label}',
                                       'user_forms': user_forms})

                # Create a FormSubmission instance
                form_submission = FormSubmission(
                    user_form=selected_form,  # Use the selected form
                    data=json.dumps(data_dict),  # Convert data to JSON string
                    user=request.user  # Set the current user as the submitter
                )
                form_submission.save()

            return render(request, 'app1/import.html', {'success': 'Data imported successfully!', 'user_forms': user_forms})

        except Exception as e:
            # Debugging: Print exception details
            print("Exception:", str(e))
            return render(request, 'app1/import.html', {'error': f'Error importing data: {str(e)}', 'user_forms': user_forms})

    # Handle GET requests
    return render(request, 'app1/import.html', {'user_forms': user_forms})

@login_required(login_url='login')
def dashboard(request):
    # Get the logged-in user's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Fetch form submissions for the logged-in user
    submissions = FormSubmission.objects.filter(user=request.user)
    accepted_submissions = FormSubmission.objects.filter(user=request.user, status='accepted').count()
    rejected_submissions = FormSubmission.objects.filter(user=request.user, status='rejected').count()

    # Prepare data for the line chart
    granularity = request.GET.get('granularity', 'month')  # Default to month
    today = datetime.now()

    if granularity == 'day':
        # Get the last 30 days
        start_date = today - timedelta(days=30)
        monthly_data = (
            submissions
            .filter(submitted_at__gte=start_date)
            .annotate(day=TruncDay('submitted_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        labels = [data['day'].strftime('%d') for data in monthly_data]  # Show days of the month
    elif granularity == 'year':
        # Get the last 5 years
        start_date = today - timedelta(days=5*365)
        monthly_data = (
            submissions
            .filter(submitted_at__gte=start_date)
            .annotate(year=TruncYear('submitted_at'))
            .values('year')
            .annotate(count=Count('id'))
            .order_by('year')
        )
        labels = [data['year'].strftime('%Y') for data in monthly_data]
    else:  # Default to month
        # Get the last 12 months
        start_date = today - timedelta(days=365)
        monthly_data = (
            submissions
            .filter(submitted_at__gte=start_date)
            .annotate(month=TruncMonth('submitted_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        labels = [data['month'].strftime('%B') for data in monthly_data]  # Show month names

    # Create a dictionary to hold counts for each label
    counts_dict = {label: 0 for label in labels}

    # Fill in the counts from the monthly_data
    for data in monthly_data:
        if granularity == 'day':
            counts_dict[data['day'].strftime('%d')] = data['count']
        elif granularity == 'year':
            counts_dict[data['year'].strftime('%Y')] = data['count']
        else:  # Default to month
            counts_dict[data['month'].strftime('%B')] = data['count']

    # Create the counts list based on the labels
    counts = [counts_dict[label] for label in labels]

    context = {
        'user_profile': user_profile,
        'status_counts': {
            'pending': submissions.filter(status='pending').count(),
            'accepted': submissions.filter(status='accepted').count(),
            'rejected': submissions.filter(status='rejected').count(),
        },
        'submissions': submissions,
        'total_submissions': submissions.count(),
        'accepted_submissions': submissions.filter(status='accepted').count(),
        'rejected_submissions': submissions.filter(status='rejected').count(),
        'labels': labels,
        'counts': counts,
        'granularity': granularity,
    }
    return render(request, 'charts/staff_dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','staff'])
def accept_submission(request, submission_id):
    if request.method == 'POST':
        try:
            submission = FormSubmission.objects.get(id=submission_id)
            submission.status = 'accepted'
            submission.save()
            return JsonResponse({'success': True})
        except FormSubmission.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Submission not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','staff'])
def reject_submission(request, submission_id):
    if request.method == 'POST':
        try:
            submission = FormSubmission.objects.get(id=submission_id)
            submission.status = 'rejected'
            submission.save()
            # Optionally, notify the user about the rejection
            # send_notification_to_user(submission.user, submission)
            return JsonResponse({'success': True})
        except FormSubmission.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Submission not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})



def bulk_accept_submissions(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        submission_ids = data.get('submission_ids', [])
        FormSubmission.objects.filter(id__in=submission_ids).update(status='accepted')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@csrf_exempt
def bulk_reject_submissions(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        submission_ids = data.get('submission_ids', [])
        FormSubmission.objects.filter(id__in=submission_ids).update(status='rejected')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@csrf_exempt
def bulk_delete(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_ids = data.get('selected_ids', [])
            FormSubmission.objects.filter(id__in=selected_ids).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# views.py  to dynamically generate the signed URL for the dashboard
# Constants
METABASE_SITE_URL = "http://localhost:5003"
METABASE_SECRET_KEY = "abef27c86994e5a767f1b3c44b7081d52c6865c620d94e24c593ec806a444082"

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def ME_Dashboard(request):
    # Payload for the JWT
    payload = {
        "resource": {"dashboard": 33},
        "params": {},
        "exp": round(time.time()) + (60 * 10) # 10 minute expiration
        }
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

    # Create the iframe URL
    iframe_url = f"{METABASE_SITE_URL}/embed/dashboard/{token}#bordered=true&titled=true"

    # Debugging line
    print("Generated iframe URL:", iframe_url)

    # Render the template with the iframe URL
    return render(request, 'app1/MEdashboard.html', {'iframe_url': iframe_url})

def get_patient_by_referral(request, referral_number):
    try:
        patient = PatientDemographics.objects.get(referral_number=referral_number)
        data = {
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'age': patient.age,
            'gender': patient.gender,
            'marital_status': patient.marital_status,
            'education_level': patient.education_level,
            'employment_status': patient.employment_status,
            'address': patient.address,
            'phone_number': patient.phone_number,
            'diagnosis': patient.diagnosis,
        }
        return JsonResponse(data)
    except PatientDemographics.DoesNotExist:
        return JsonResponse({'error': 'Patient not found.'}, status=404)

@receiver(post_save, sender=PatientDemographics)
def log_patient_update(sender, instance, **kwargs):
    AuditLog.objects.create(
        user=instance.updated_by,
        action=f"Updated patient {instance.referral_number}",
        timestamp=timezone.now()
    )

def patient_search(request):
    query = request.GET.get('q', '')
    if query:
        patients = Patient.objects.filter(
            Q(referral_number__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        if patients.exists():
            patient = patients.first()
            data = {
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'gender': patient.gender,
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'Patient not found.'}, status=404)
    return JsonResponse({'error': 'No search query provided.'}, status=400)
