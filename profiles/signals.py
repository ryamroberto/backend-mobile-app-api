from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .services import profile_services

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile_services.profile_create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        profile_services.profile_create(user=instance)
    else:
        instance.profile.save()
