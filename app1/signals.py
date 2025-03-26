# To automatically create or update the UserProfile whenever a User is created or updated

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User,Group
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Create profile if it doesn't exist
    UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def add_to_staff_group(sender, instance, created, **kwargs):
    if instance.is_staff:
        staff_group = Group.objects.get(name='staff')
        instance.groups.add(staff_group)

     #TO AUTOMATICALLY ADD ADMIN USERS TO THE ADMIN GROUP
@receiver(post_save, sender=User)
def handle_admin_group(sender, instance, **kwargs):
    """Sync admin group with is_staff status"""
    admin_group = Group.objects.get(name='admin')
    if instance.is_staff:
        instance.groups.add(admin_group)
    else:
        instance.groups.remove(admin_group)