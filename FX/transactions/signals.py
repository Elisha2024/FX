from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserCurrencyPreference

@receiver(post_save, sender=User)
def create_user_currency_preference(sender, instance, created, **kwargs):
    """
    Create a UserCurrencyPreference instance when a User is created.
    This signal is triggered after a new User is saved.
    """
    if created:
        UserCurrencyPreference.objects.create(user=instance)
