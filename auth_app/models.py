from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model.

    Overrides the default user manager to use email instead of username
    as the unique identifier for authentication.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.

        Args:
            email (str): The user's email address (required).
            password (str, optional): The user's password.
            extra_fields (dict): Any additional user fields.

        Returns:
            CustomUser: The created user instance.

        Raises:
            ValueError: If email is not provided.
        """

        if not email:
            raise ValueError('The e-mail address must be entered.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.

        Ensures that is_staff, is_superuser, and is_active are all set to True.

        Args:
            email (str): The superuser's email.
            password (str, optional): The superuser's password.
            extra_fields (dict): Any additional fields.

        Returns:
            CustomUser: The created superuser instance.

        Raises:
            ValueError: If is_staff or is_superuser is not set to True.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """
    Custom user model that uses email instead of username for authentication.

    Fields:
        - email (unique): Used as the primary identifier.
        - fullname: The user's full name.
    Removes the default 'username' field provided by AbstractUser.
    """

    username = None
    email = models.EmailField('email address', unique=True)
    fullname = models.CharField(max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager() 

    def __str__(self):
        """
        String representation of the user.

        Returns:
            str: The user's email address.
        """
        
        return self.email
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["email"]  