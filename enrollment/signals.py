from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Inscription


@receiver(post_save, sender=User)
def create_inscription(sender, instance, created, **kwargs):

    if created:
        Inscription.objects.create(user=instance)