from django.urls import path
from . import views
from .views import review_submissions, ReviewRecords, \
    import_data, edit_submission, dashboard, submissions_list, user_submissions, update_submission, \
    bulk_accept_submissions, bulk_reject_submissions, unauthorized, ME_Dashboard,bulk_delete, get_patient_by_referral, patient_search
#from Landing_page import views as landing_views
#app_name = 'app2'

urlpatterns = [
    # user's side
    path('', views.index, name='index'),
    path('login', views.loginpage, name='login'),
    path('forgot_password', views.export_data, name='forgot_password'),
    path('reset_password', views.export_data, name='reset_password'),
    path('export_data', views.export_data, name='export_data'),
    path('unauthorized/', unauthorized, name='unauthorized'),
    path('logout', views.logoutuser, name='logout'),
    path('register', views.register, name='register'),
    path('me_dashboard/', ME_Dashboard, name='me_dashboard'),
    # staff dashboard
    path('dashboard/', dashboard, name='dashboard'),

    path('add_user/', views.add_user, name='add_user'),
    path('enter_data/', views.enter_data, name='enter_data'),
    path('predictive_analytics/', views.predictive_analytics, name='predictive_analytics'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('Forms/', views.Forms, name='Forms'),
    path('form_submissions/ReviewRecords/<int:submission_id>/', views.ReviewRecords, name='ReviewRecords'), #    path('form_submissions/update/<int:form_id>/', get_form_submissions, name='get_form_submissions'),

    path('api/patient-by-referral/<str:referral_number>/', get_patient_by_referral, name='get_patient_by_referral'),
    path('api/patient-search/', patient_search, name='patient_search'),

    path('create_user_form/', views.create_user_form, name='create_user_form'),
    path('create_user_form_field/<int:form_id>/', views.create_user_form_field, name='create_user_form_field'),
    path('edit_user_form/<int:form_id>/', views.edit_user_form, name='edit_user_form'),
    path('user_forms_list/', views.user_forms_list, name='user_forms_list'),
    path('form_fields_list/<int:form_id>/', views.form_fields_list, name='form_fields_list'),
    path('form_view/<int:form_id>/', views.form_view, name='form_view'),
    path('form_submission_success/', views.form_submission_success, name='form_submission_success'),
    path('list_form_submissions/', views.list_form_submissions, name='list_form_submissions'),
    path('delete_user_form/<int:form_id>/', views.delete_user_form, name='delete_user_form'),
    path('fill_form/<int:form_id>/', views.fill_form, name='fill_form'),

    path('user/<int:user_id>/submissions/', views.review_submissions, name='review_submissions'),

    #for exporting forms
    path('Submissions/', views.submissions, name='Submissions'),
    path('submissions/edit/<int:submission_id>/', edit_submission, name='edit_submission'),
   # for imports
    path('import/', import_data, name='import_data'),
    path('update_submission/<int:submission_id>/', views.update_submission, name='update_submission'),
    path('form-submissions/update/<int:submission_id>/', views.update_submission, name='update_submission'),
    path('submissions/', submissions_list, name='submissions_list'),
    path('submissions/user/<int:user_id>/', user_submissions, name='user_submissions'),

    path('accept-submission/<int:submission_id>/', views.accept_submission, name='accept_submission'),
    path('reject-submission/<int:submission_id>/', views.reject_submission, name='reject_submission'),
    path('bulk-accept-submissions/', bulk_accept_submissions, name='bulk_accept_submissions'),
    path('bulk-reject-submissions/', bulk_reject_submissions, name='bulk_reject_submissions'),
    path('bulk-delete/', bulk_delete, name='bulk_delete'),
]
