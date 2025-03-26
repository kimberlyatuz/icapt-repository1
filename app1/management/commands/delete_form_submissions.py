from django.core.management.base import BaseCommand
from app1.models import FormSubmission  # Replace with your actual model

class Command(BaseCommand):
    help = 'Delete FormSubmission records based on title'

    def add_arguments(self, parser):
        parser.add_argument('title', type=str, help='Quality of Care dataset for HIV clients')

    def handle(self, *args, **kwargs):
        title = kwargs['title']

        # Filter and delete records based on the specific title
        deleted_count, _ = FormSubmission.objects.filter(title=title).delete()
        print(f'Deleted {deleted_count} form submissions with title: {title}')