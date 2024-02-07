from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from communications.models import UserContactInfo


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserContactInfo.objects.create(user=instance)
    else:
        instance.userprofile.save()
