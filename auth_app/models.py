from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    fullname = models.CharField(max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # oder ['fullname'], falls nötig

    def __str__(self):
        return self.email