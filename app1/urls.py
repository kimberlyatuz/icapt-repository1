from django.urls import path
from .views import process_document
from . import views
from .views import (review_submissions, ReviewRecords, \
    import_data, form_view, add_patient, edit_submission, dashboard, submissions_list, user_submissions, update_submission, \
    bulk_accept_submissions, LoginView, bulk_reject_submissions, unauthorized, ME_Dashboard,bulk_delete, fetch_patient, patient_search, PasswordResetView)


urlpatterns = [
# Authentication
    path('login/', views.loginpage, name='login'),
    path('register/', views.register,name='register'),
    path('logout/', views.logoutuser, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('password-reset/', views.PasswordResetView, name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.PasswordResetConfirmView, name='password_reset_confirm'),
    path('password-reset-complete/', views.PasswordResetCompleteView,name='password_reset_complete'),
    # Main pages
    path('', views.index, name='index'),
    path('unauthorized/', unauthorized, name='unauthorized'),
    path('me_dashboard/', ME_Dashboard, name='me_dashboard'),
    path('dashboard/', dashboard, name='dashboard'),
    path('predictive_analytics/', views.predictive_analytics, name='predictive_analytics'),

    # Form management
    path('Forms/', views.Forms, name='Forms'),
    path('create_user_form/', views.create_user_form, name='create_user_form'),
    path('create_user_form_field/<int:form_id>/', views.create_user_form_field, name='create_user_form_field'),
    path('edit_user_form/<int:form_id>/', views.edit_user_form, name='edit_user_form'),
    path('user_forms_list/', views.user_forms_list, name='user_forms_list'),
    path('delete_user_form/<int:form_id>/', views.delete_user_form, name='delete_user_form'),
    path('form_fields_list/<int:form_id>/', views.form_fields_list, name='form_fields_list'),
    path('process-document/', process_document, name='process_document'),
    path('form/<int:form_id>/', form_view, name='form_view'),

    path('fill_form/<int:form_id>/', views.fill_form, name='fill_form'),
    path('enter_data/', views.enter_data, name='enter_data'),
    path('form_submissions/ReviewRecords/<int:submission_id>/', ReviewRecords, name='ReviewRecords'),
    # for the picture imports
    path('upload/', views.upload_and_extract, name='upload'),
    path('result/<int:pk>/', views.result_view, name='result'),

    # User /Patient management
    path('add_user/', views.add_user, name='add_user'),
    path('add-patient/', add_patient, name='add_patient'),
    path('patient-demographics/', views.save_patient_demographics, name='save_patient_demographics'),

    # Data operations
    path('import/', import_data, name='import_data'),
    path('export_data/', views.export_data, name='export_data'),

    # Submission handling
    path('form_submission_success/', views.form_submission_success, name='form_submission_success'),
    path('list_form_submissions/', views.list_form_submissions, name='list_form_submissions'),
    path('submissions/', submissions_list, name='submissions_list'),
    path('user/<int:user_id>/submissions/', views.review_submissions, name='review_submissions'),
    path('Submissions/', views.submissions, name='Submissions'),
    path('submissions/edit/<int:submission_id>/', edit_submission, name='edit_submission'),
    path('submissions/user/<int:user_id>/', user_submissions, name='user_submissions'),
    path('update_submission/<int:submission_id>/', update_submission, name='update_submission'),
    path('form-submissions/update/<int:submission_id>/', views.update_submission, name='update_submission'),

    # API endpoints
    #path('api/patient-by-referral/<str:referral_number>/', get_patient_by_referral, name='get_patient_by_referral'),
    path('fetch-patient/', fetch_patient, name='fetch_patient'),
    path('api/patient-search/', patient_search, name='patient_search'),
    path('api/patient-search/', patient_search, name='patient_search'),

    # Bulk operations
    path('accept-submission/<int:submission_id>/', views.accept_submission, name='accept_submission'),
    path('reject-submission/<int:submission_id>/', views.reject_submission, name='reject_submission'),
    path('bulk-accept-submissions/', bulk_accept_submissions, name='bulk_accept_submissions'),
    path('bulk-reject-submissions/', bulk_reject_submissions, name='bulk_reject_submissions'),
    path('bulk-delete/', bulk_delete, name='bulk_delete'),
]
