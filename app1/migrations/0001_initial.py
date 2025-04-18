# Generated by Django 4.2.19 on 2025-03-05 18:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Form',
                'verbose_name_plural': 'User Forms',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, null=True)),
                ('phone', models.CharField(max_length=300, null=True)),
                ('email', models.CharField(max_length=300, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFormField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=100)),
                ('field_type', models.CharField(max_length=20, null=True)),
                ('required', models.BooleanField(default=False)),
                ('options', models.TextField(blank=True, help_text='Comma-separated options for radio/checkbox/select fields')),
                ('placeholder', models.CharField(blank=True, max_length=100)),
                ('order', models.IntegerField(default=0)),
                ('help_text', models.TextField(blank=True)),
                ('css_class', models.CharField(blank=True, max_length=100, null=True)),
                ('position', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='app1.userform')),
            ],
            options={
                'verbose_name': 'User Form Field',
                'verbose_name_plural': 'User Form Fields',
            },
        ),
        migrations.CreateModel(
            name='FormSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('form_id', models.CharField(max_length=255, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=50)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app1.userform')),
            ],
            options={
                'verbose_name': 'Form Submission',
                'verbose_name_plural': 'Form Submissions',
                'db_table': 'form_submissions',
                'ordering': ['-submitted_at'],
                'unique_together': {('user_form', 'submitted_at')},
            },
        ),
    ]
