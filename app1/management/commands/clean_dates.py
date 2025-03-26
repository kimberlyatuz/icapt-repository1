from datetime import datetime, timedelta
from dateutil import parser
from django.core.management.base import BaseCommand
from app1.models import FormSubmission  # Replace with your actual model


class Command(BaseCommand):
    help = 'Clean and standardize date fields in FormSubmission model'

    def handle(self, *args, **kwargs):
        records = FormSubmission.objects.all()  # Fetch all FormSubmission records
        for record in records:
            original_date = record.data  # Replace with your actual date field name

            if isinstance(original_date, str):
                try:
                    # Attempt to parse the date
                    standardized_date = parser.parse(original_date)
                    record.data = standardized_date  # Set the standardized date
                except ValueError:
                    print(f'Could not parse date for record {record.id}: {original_date}')

            elif isinstance(original_date, (int, float)):  # Check for serial date formats
                # Convert Excel serial date to Python datetime
                standardized_date = datetime(1899, 12, 30) + timedelta(days=original_date)
                record.data = standardized_date  # Set the standardized date

            # Save the updated record if a change was made
            record.save()  # Save if there were any changes
            print(f'Updated record {record.id}: {original_date} -> {record.data}')