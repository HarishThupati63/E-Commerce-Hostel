from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    college_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
