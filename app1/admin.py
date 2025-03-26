from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from import_export.admin import ImportExportModelAdmin
from .models import UserForm, FormSubmission, UserFormField, PatientDemographics, UserProfile
from .forms import FormSubmissionForm, UserFormFieldCreationForm, UserFormCreationForm


class UserFormFieldInline(admin.StackedInline):
    model = UserFormField
    extra = 1  # Number of empty forms to display
    fields = ('label', 'field_type', 'required', 'options', 'placeholder')
    show_change_link = True  # Allows editing the inline object in a separate page

    def get_formset(self, request, obj=None, **kwargs):
        """Customize the formset if needed."""
        formset = super().get_formset(request, obj, **kwargs)
        return formset


# Custom Admin for FormSubmission
class FormSubmissionAdmin(ImportExportModelAdmin):
    list_display = ('user_form', 'user', 'status', 'submitted_at', 'patient')
    search_fields = ('user_form__title', 'user__username', 'patient__first_name')
    list_filter = ('status', 'user_form')
    actions = ['accept_selected', 'reject_selected', 'delete_selected']

    fieldsets = (
        ('About Form', {
            'fields': ('status', 'patient', 'data'),
        }),
        ('Form Data', {
            'fields': ('feedback',),
        }),
    )

    def data(self, obj):
        """Render the data field as an HTML table, handling nested JSON."""
        if obj.data:
            try:
                data_dict = obj.data
                table_html = "<table class='table table-striped'><thead><tr>"
                for key in data_dict.keys():
                    table_html += f"<th>{key}</th>"
                table_html += "</tr></thead><tbody><tr>"
                for value in data_dict.values():
                    if isinstance(value, (dict, list)):
                        table_html += f"<td>{json.dumps(value)}</td>"
                    else:
                        table_html += f"<td>{value}</td>"
                table_html += "</tr></tbody></table>"
                return format_html(table_html)
            except Exception as e:
                return f"Error rendering data: {str(e)}"
        return "No Data"

    def accept_selected(self, request, queryset):
        """Mark selected submissions as accepted."""
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} submissions were successfully marked as accepted.')

    accept_selected.short_description = 'Accept selected submissions'

    def reject_selected(self, request, queryset):
        """Mark selected submissions as rejected."""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} submissions were successfully marked as rejected.')

    reject_selected.short_description = 'Reject selected submissions'

    def delete_selected(self, request, queryset):
        """Delete selected form submissions."""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Deleted {count} selected form submissions.')

    delete_selected.short_description = 'Delete selected form submissions'


class UserFormAdmin(admin.ModelAdmin):
    list_display = ('title_link', 'creator', 'created_at')  # Use title_link for clickable title
    search_fields = ('title', 'creator__username')
    list_filter = ('creator', 'created_at')  # Add filters for creator and creation date
    inlines = [UserFormFieldInline]  # Show fields inline

    def title_link(self, obj):
        # Link to the edit view of the UserForm
        url = reverse('admin:app1_userform_change', args=[obj.id])  # Edit view URL
        return format_html('<a href="{}">{}</a>', url, obj.title)

    title_link.short_description = 'Title'

    def get_urls(self):
        # Add custom URL for the submissions view
        urls = super().get_urls()
        custom_urls = [
            path('submissions/<int:form_id>/', self.admin_site.admin_view(self.submissions_view), name='form_submissions'),
        ]
        return custom_urls + urls

    def submissions_view(self, request, form_id):
        # Fetch the form and its submissions
        user_form = get_object_or_404(UserForm, id=form_id)
        submissions = FormSubmission.objects.filter(user_form=user_form).select_related('user')

        # Prepare submission data for the template
        submission_data = []
        for submission in submissions:
            submission_data.append({
                'user': submission.user.username,
                'status': submission.status,
                'submitted_at': submission.submitted_at,
                'data': submission.get_data()  # Get the parsed data (dictionary)
            })

        # Pass data to the template
        context = {
            'user_form': user_form,
            'submissions': submission_data,  # Pass the structured data to the template
        }
        return render(request, 'charts/form_data.html', context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Add a link to the submissions view in the edit view
        extra_context = extra_context or {}
        extra_context['submissions_url'] = reverse('admin:form_submissions', args=[object_id])
        return super().change_view(request, object_id, form_url, extra_context)


# Custom Admin for PatientDemographics
@admin.register(PatientDemographics)
class PatientDemographicsAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'referral_number', 'age', 'gender', 'diagnosis', 'created_at')
    search_fields = ('first_name', 'last_name', 'referral_number', 'diagnosis')
    list_filter = ('gender', 'marital_status', 'education_level', 'employment_status')
    raw_id_fields = ('updated_by',)  # Improve performance for selecting users


# Custom Admin for UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name','email', 'date_created')
    search_fields = ('user__username', 'email')

# Register the models with their custom admin classes
admin.site.register(UserForm, UserFormAdmin)
admin.site.register(FormSubmission, FormSubmissionAdmin)