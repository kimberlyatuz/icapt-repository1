from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from .models import UserForm, UserFormField, FormSubmission, UserProfile, PatientDemographics

# Form for PatientDemographics
class PatientDemographicsForm(forms.ModelForm):
    class Meta:
        model = PatientDemographics
        fields = '__all__'

# Form for UserForm creation
class UserFormCreationForm(forms.ModelForm):
    class Meta:
        model = UserForm
        fields = '__all__'

# Form for UserFormField creation
class UserFormFieldCreationForm(forms.ModelForm):
    class Meta:
        model = UserFormField
        fields = '__all__'

# Form for FormSubmission
class FormSubmissionForm(forms.ModelForm):
    class Meta:
        model = FormSubmission
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        if self.instance.patient:
            self.fields['patient'].widget.attrs['readonly'] = True

# Form for importing data
class ImportForm(forms.Form):
    file = forms.FileField()

# Form for user creation
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
            ),
            Row(
                Column('password1', css_class='col-md-6'),
                Column('password2', css_class='col-md-6'),
            ),
            Submit('submit', 'Register', css_class='btn btn-primary')
        )

# Form for UserProfile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
            ),
            Row(
                Column('email', css_class='col-md-6'),
            ),
            Submit('submit', 'Save', css_class='btn btn-primary')
        )