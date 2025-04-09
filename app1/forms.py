from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from .models import UserForm, UserFormField, FormSubmission, UserProfile, PatientDemographics
# for image uploads
import pytesseract
from PIL import Image
from django.core.exceptions import ValidationError
import pandas as pd
from .models import ExtractedImage

# Form for PatientDemographics
class PatientDemographicsForm(forms.ModelForm):
    class Meta:
        model = PatientDemographics
        fields = '__all__'
         #for form validations
        def clean(self):
            cleaned_data = super().clean()
            age = cleaned_data.get('age')
            marital_status = cleaned_data.get('marital_status')
            employment_status = cleaned_data.get('employment_status')

            if age is not None and marital_status == 'married' and age < 18:
                self.add_error('marital_status', 'Minors cannot be marked as married')

            if employment_status == 'retired' and (age is None or age < 50):
                self.add_error('employment_status', 'Retired status unlikely for people under 50')

#user creation form
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

# Form for UserForm creation
class UserFormCreationForm(forms.ModelForm):
    class Meta:
        model = UserForm
        fields = '__all__'

        def clean(self):
            cleaned_data = super().clean()
            title = cleaned_data.get('title')
            if title and len(title) < 3:
                self.add_error('title', 'Title must be at least 3 characters long')

# Form for UserFormField creation
class UserFormFieldCreationForm(forms.ModelForm):
    class Meta:
        model = UserFormField
        fields = '__all__'
        #validations
        def clean(self):
            cleaned_data = super().clean()
            field_type = cleaned_data.get('field_type')
            options = cleaned_data.get('options')

            if field_type in ['select', 'checkbox', 'radio'] and not options:
                self.add_error('options', 'Options are required for select, checkbox, and radio field types')

            if field_type not in ['select', 'checkbox', 'radio'] and options:
                self.add_error('options', 'Options should only be provided for select, checkbox, and radio field types')


# Form for FormSubmission
class FormSubmissionForm(forms.ModelForm):
    document_upload = forms.ImageField(
        required=False,
        label="Upload Document",
        help_text="Upload a document image to extract data (optional)"
    )
    extracted_data_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = FormSubmission
        fields = '__all__'
        widgets = {
            'data': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.CharField):
                field.widget.attrs.update({
                    'data-validation-type': 'alphanumeric'
                })
            elif isinstance(field, forms.IntegerField):
                field.widget.attrs.update({
                    'data-validation-type': 'number',
                    'min': 0  # Set appropriate min/max values
                })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('document_upload'),
            HTML("""
            <div id="ocr-preview" class="card mb-3" style="display:none;">
                <div class="card-header">
                    <h5 class="mb-0">Extracted Data</h5>
                </div>
                <div class="card-body">
                    <div id="extracted-fields" class="mb-3"></div>
                    <button type="button" id="use-extracted-data" class="btn btn-secondary">
                        Use Extracted Data
                    </button>
                </div>
            </div>
            """),
            Field('extracted_data_json', type="hidden"),
            Field('data'),
            Field('status'),
            Field('feedback'),
            Submit('submit', 'Submit', css_class='btn btn-primary')
        )

        if self.instance.patient:
            self.fields['patient'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        document_upload = cleaned_data.get('document_upload')
        extracted_data_json = cleaned_data.get('extracted_data_json')
        data = cleaned_data.get('data')

        # Process document upload if provided
        if document_upload:
            try:
                img = Image.open(document_upload)
                extracted_text = pytesseract.image_to_string(img)

                # Parse the extracted text into a structured format
                parsed_data = self.parse_extracted_text(extracted_text)
                cleaned_data['extracted_data_json'] = json.dumps(parsed_data)

                # Store the parsed data in the form instance for the template
                self.extracted_data = parsed_data
            except Exception as e:
                self.add_error('document_upload', f'Error processing document: {str(e)}')

        # If we have extracted data that was confirmed by the user
        if extracted_data_json and not data:
            try:
                data_dict = json.loads(extracted_data_json)
                cleaned_data['data'] = json.dumps(data_dict)
            except json.JSONDecodeError:
                self.add_error('extracted_data_json', 'Invalid extracted data format')

        # Your existing validation
        if not cleaned_data.get('data'):
            self.add_error('data', 'Submission data cannot be empty')

        if cleaned_data.get('status') == 'rejected' and not cleaned_data.get('feedback'):
            self.add_error('feedback', 'Feedback is required when rejecting a submission')

        return cleaned_data

    def parse_extracted_text(self, text):
        """Convert OCR-extracted text into structured data"""
        # This is a simple example - you'll need to customize based on your form fields
        data = {}
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Simple pattern matching - adjust based on your document format
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                data[key] = value.strip()
            elif '=' in line:
                key, value = line.split('=', 1)
                key = key.strip().lower().replace(' ', '_')
                data[key] = value.strip()

        return data


# Form for importing data
class ImportForm(forms.Form):
    file = forms.FileField(
        required=False,
        label="CSV/Excel File",
        help_text="Upload CSV or Excel file for direct import"
    )
    image = forms.ImageField(
        required=False,
        label="Image/PDF Document",
        help_text="Upload an image or PDF to extract data using OCR"
    )
    extracted_data = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    confirmed_data = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('file', css_class='col-md-6'),
                Column('image', css_class='col-md-6'),
            ),
            HTML("""
            <div id="preview-section" class="mt-3" style="display:none;">
                <h4>Extracted Data Preview</h4>
                <div id="data-preview" class="card mb-3"></div>
                <button type="button" id="edit-data" class="btn btn-secondary">Edit Data</button>
                <div id="edit-section" style="display:none;">
                    <textarea id="data-editor" class="form-control mb-2" rows="10"></textarea>
                    <button type="button" id="save-edit" class="btn btn-primary">Save Changes</button>
                </div>
            </div>
            """),
            'extracted_data',
            'confirmed_data',
            Submit('submit', 'Process Data', css_class='btn btn-primary mt-3')
        )

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        image = cleaned_data.get('image')
        confirmed_data = cleaned_data.get('confirmed_data')

        if not file and not image and not confirmed_data:
            raise ValidationError('Either a file or an image must be uploaded.')

        if file and image:
            raise ValidationError('Please upload either a file or an image, not both.')

        if file:
            self.clean_file(file)

        if image and not confirmed_data:
            # Process image only if we don't have confirmed data already
            text = self.clean_image(image)
            cleaned_data['extracted_data'] = text
            self.data = self.data.copy()  # Make data mutable
            self.data['extracted_data'] = text

        if confirmed_data:
            try:
                # Validate the confirmed JSON data
                data = json.loads(confirmed_data)
                if not isinstance(data, dict):
                    raise ValidationError('Invalid data format')
            except json.JSONDecodeError:
                raise ValidationError('Invalid JSON data')

        return cleaned_data

    def clean_file(self, file):
        if not (file.name.endswith('.csv') or file.name.endswith('.xlsx')):
            raise ValidationError('File must be a CSV or Excel (.xlsx) file.')

        try:
            if file.name.endswith('.csv'):
                data = pd.read_csv(file)
            else:
                data = pd.read_excel(file)
        except Exception as e:
            raise ValidationError(f'Error reading file: {e}')

        self.validate_import_data(data)

    def clean_image(self, image):
        if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            raise ValidationError('File must be a PNG, JPG, JPEG, or PDF.')

        try:
            if image.name.lower().endswith('.pdf'):
                # For PDFs, we'll use pdf2image to convert to images first
                images = convert_from_bytes(image.read())
                full_text = ""
                for img in images:
                    text = pytesseract.image_to_string(img)
                    full_text += text + "\n"
            else:
                # For regular images
                img = Image.open(image)
                full_text = pytesseract.image_to_string(img)

            return full_text
        except Exception as e:
            raise ValidationError(f'Error processing image: {str(e)}')

    def validate_import_data(self, data):
        required_columns = ['first_name', 'last_name', 'age', 'gender']
        missing_columns = [col for col in required_columns if col.lower() not in map(str.lower, data.columns)]

        if missing_columns:
            raise ValidationError(f'Missing required columns: {", ".join(missing_columns)}')

        for col in required_columns:
            if col.lower() in map(str.lower, data.columns):
                if data[col].isnull().any() or (data[col] == '').any():
                    raise ValidationError(f'Column "{col}" cannot have blank values.')


# Form for UserProfile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

        #validations
        def clean(self):
            cleaned_data = super().clean()
            email = cleaned_data.get('email')
            if email and User.objects.filter(email=email).exists():
                self.add_error('email', 'This email is already in use by another user')


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


class ExtractedImageForm(forms.ModelForm):
    class Meta:
        model = ExtractedImage
        fields = ('image',)

