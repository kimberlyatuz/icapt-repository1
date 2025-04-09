from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import date
import json
import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# PatientDemographics model
class PatientDemographics(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    EDUCATION_LEVEL_CHOICES = [
        ('none', 'None'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('tertiary', 'Tertiary'),
    ]
    EMPLOYMENT_STATUS_CHOICES = [
        ('employed', 'Employed'),
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
        ('retired', 'Retired'),
    ]

    first_name = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                r'^[a-zA-Z\s\-\.\']+$',
                _('Only letters, spaces, hyphens, periods, and apostrophes are allowed in names')
            )
        ]
    )
    last_name = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                r'^[a-zA-Z\s\-\.\']+$',
                _('Only letters, spaces, hyphens, periods, and apostrophes are allowed in names')
            )
        ]
    )
    referral_number = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0, _('Age cannot be negative')),
            MaxValueValidator(120, _('Please enter a valid age (0-120)'))
        ]
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    education_level = models.CharField(max_length=10, choices=EDUCATION_LEVEL_CHOICES)
    employment_status = models.CharField(max_length=10, choices=EMPLOYMENT_STATUS_CHOICES)
    address = models.TextField(
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9\s\.,#\-]+$',
                _('Only alphanumeric characters and basic punctuation are allowed in addresses')
            )
        ]
    )
    phone_number = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                r'^\+?[0-9]{8,15}$',
                _('Enter a valid phone number (8-15 digits, optional + prefix)')
            )
        ]
    )
    diagnosis = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_patients')

    def clean(self):
        super().clean()
        # Additional validation that requires access to multiple fields
        if self.age < 18 and self.marital_status == 'married':
            raise ValidationError({
                'marital_status': _('Minors cannot be marked as married')
            })
        if self.employment_status == 'retired' and self.age < 50:
            raise ValidationError({
                'employment_status': _('Retired status unlikely for people under 50')
            })

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.referral_number})"


# UserForm model
class UserForm(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=300,
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9\s\-\_\.\(\)]+$',
                _('Only alphanumeric characters, spaces, hyphens, underscores, periods and parentheses are allowed in titles')
            )
        ]
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if len(self.title) < 5:
            raise ValidationError({
                'title': _('Title must be at least 5 characters long')
            })

    class Meta:
        verbose_name = "User Form"
        verbose_name_plural = "User Forms"

    def __str__(self):
        return self.title


# UserFormField model
class UserFormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('textarea', 'Textarea'),
        ('select', 'Select'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio Button'),
        ('date', 'Date'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    user_form = models.ForeignKey(UserForm, related_name='fields', on_delete=models.CASCADE)
    label = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9\s\-\_]+$',
                _('Only alphanumeric characters, spaces, hyphens and underscores are allowed in labels')
            )
        ]
    )
    field_type = models.CharField(max_length=20, null=True, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    options = models.TextField(
        blank=True,
        help_text="Comma-separated options for radio/checkbox/select fields",
        validators=[
            RegexValidator(
                r'^[^,]+(,[^,]+)*$',
                _('Options must be comma-separated without trailing commas')
            )
        ]
    )
    placeholder = models.CharField(
        max_length=100,
        blank=True,
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9\s\-\_\.\,\!\?]+$',
                _('Only alphanumeric characters and basic punctuation are allowed in placeholders')
            )
        ]
    )

    def clean(self):
        super().clean()
        if self.field_type in ['select', 'checkbox', 'radio'] and not self.options:
            raise ValidationError({
                'options': _('Options are required for select, checkbox, and radio field types')
            })
        if self.field_type not in ['select', 'checkbox', 'radio'] and self.options:
            raise ValidationError({
                'options': _('Options should only be provided for select, checkbox, and radio field types')
            })

    def get_options(self):
        return [opt.strip() for opt in self.options.split(',')] if self.options else []

    class Meta:
        verbose_name = 'User Form Field'
        verbose_name_plural = 'User Form Fields'
        ordering = ['id']

    def __str__(self):
        return self.label


# FormSubmission model
class FormSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]

    user_form = models.ForeignKey(UserForm, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientDemographics, on_delete=models.CASCADE, blank=True, null=True)
    data = models.JSONField()  # To store submitted data as JSON
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    form_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True)

    def clean(self):
        super().clean()
        if not self.data:
            raise ValidationError({'data': _('Submission data cannot be empty')})

        if self.status == 'rejected' and not self.feedback:
            raise ValidationError({
                'feedback': _('Feedback is required when rejecting a submission')
            })

    def get_data(self):
        """Ensure data is always returned as a dictionary."""
        if isinstance(self.data, str):
            try:
                return json.loads(self.data)
            except json.JSONDecodeError:
                return {}
        return self.data or {}

    class Meta:
        db_table = 'form_submissions'
        ordering = ['-submitted_at']
        verbose_name = 'Form Submission'
        verbose_name_plural = 'Form Submissions'
        unique_together = ('user_form', 'submitted_at')

    def __str__(self):
        return f"Submission by {self.user.username} on {self.submitted_at}"

    def save(self, *args, **kwargs):
        # Validate data before saving
        if isinstance(self.data, dict):
            for key, value in self.data.items():
                if isinstance(value, date):
                    self.data[key] = value.isoformat()

        if self.pk:  # Only for existing instances
            original = FormSubmission.objects.get(pk=self.pk)
            if not original.is_editable() and self.status == original.status:
                raise ValidationError("Cannot modify a processed submission")

        super().save(*args, **kwargs)

    def update_field(self, field_name, new_value):
        """Safely update a single field in the submission data"""
        if not self.is_editable():
            raise ValidationError(_('Cannot update a processed submission'))

        data = self.get_data()
        if field_name in data:
            data[field_name] = new_value
            self.data = data
            self.save()
            return True
        return False

    def is_editable(self):
        """Check if submission can be edited (only in pending status)"""
        return self.status == 'pending'

# UserProfile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=300,
        null=True,
        validators=[
            RegexValidator(
                r'^[a-zA-Z\s\-\.\']+$',
                _('Only letters, spaces, hyphens, periods, and apostrophes are allowed in names')
            )
        ]
    )
    phone = models.CharField(
        max_length=300,
        null=True,
        validators=[
            RegexValidator(
                r'^\+?[0-9]{8,15}$',
                _('Enter a valid phone number (8-15 digits, optional + prefix)')
            )
        ]
    )
    email = models.CharField(
        max_length=300,
        null=True,
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                _('Enter a valid email address')
            )
        ]
    )
    date_created = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.email and User.objects.filter(email=self.email).exclude(pk=self.user.pk).exists():
            raise ValidationError({'email': _('This email is already in use by another user')})

    def __str__(self):
        return self.user.username
class ExtractedImage(models.Model):
    image = models.ImageField(upload_to='uploaded_images/')
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"

#audits
User = get_user_model()


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_display()} on {self.model_name} by {self.user}"
