import os
from django.contrib.auth import get_user_model

def run():
    User = get_user_model()
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    
    if not all([username, email, password]):
        print("Superuser environment variables not set")
        return
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser {username} created")
    else:
        print(f"Superuser {username} already exists")

if __name__ == '__main__':
    run()
