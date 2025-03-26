from django.db import models
from django.contrib.auth.models import User
from datetime import date
import json
import uuid

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

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    referral_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    education_level = models.CharField(max_length=10, choices=EDUCATION_LEVEL_CHOICES)
    employment_status = models.CharField(max_length=10, choices=EMPLOYMENT_STATUS_CHOICES)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    diagnosis = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_patients')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.referral_number})"

# UserForm model
class UserForm(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
    label = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, null=True)
    required = models.BooleanField(default=False)
    options = models.TextField(blank=True, help_text="Comma-separated options for radio/checkbox/select fields")
    placeholder = models.CharField(max_length=100, blank=True)

    def get_options(self):
        return self.options.split(',') if self.options else []

    class Meta:
        verbose_name = 'User Form Field'
        verbose_name_plural = 'User Form Fields'

    def __str__(self):
        return self.label

# FormSubmission model
class FormSubmission(models.Model):
    user_form = models.ForeignKey(UserForm, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientDemographics, on_delete=models.CASCADE, blank=True, null=True)
    data = models.JSONField()  # To store submitted data as JSON
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    form_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    feedback = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def get_data(self):
        """Ensure data is always returned as a dictionary."""
        if isinstance(self.data, str):
            try:
                return json.loads(self.data)  # Deserialize JSON string
            except json.JSONDecodeError:
                return {}
        return self.data or {}  # Return empty dict if data is None

    class Meta:
        db_table = 'form_submissions'
        ordering = ['-submitted_at']
        verbose_name = 'Form Submission'
        verbose_name_plural = 'Form Submissions'
        unique_together = ('user_form', 'submitted_at')

    def __str__(self):
        return f"Submission by {self.user.username} on {self.submitted_at}"

    def save(self, *args, **kwargs):
        # Serialize date objects in the data field before saving
        if isinstance(self.data, dict):
            for key, value in self.data.items():
                if isinstance(value, date):
                    self.data[key] = value.isoformat()  # Convert date to string
        super().save(*args, **kwargs)

    def update_field(self, field_name, new_value):
        """Safely update a single field in the submission data"""
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

#override the model's save method to prevent direct updates:
    def save(self, *args, **kwargs):
        if self.pk:  # Only for existing instances
            original = FormSubmission.objects.get(pk=self.pk)
            if not original.is_editable() and self.status == original.status:
                raise ValueError("Cannot modify a processed submission")

        super().save(*args, **kwargs)

# UserProfile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, null=True)
    phone = models.CharField(max_length=300, null=True)
    email = models.CharField(max_length=300, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username