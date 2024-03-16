from django.contrib.auth.models import AbstractUser
from django.db import models


class Member(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
