from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from pyPlants.models import AbstractPlantModel


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class PlantUser(AbstractBaseUser, PermissionsMixin, AbstractPlantModel):
    class LanguageChoices(models.TextChoices):
        ENGLISH = 'EN', 'English'
        FRENCH = 'FR', 'French'

    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(blank=True)
    default_language = models.CharField(max_length=2, choices=LanguageChoices.choices, default=LanguageChoices.ENGLISH)
    has_ai_enabled = models.BooleanField(default=False, help_text='Whether the user has AI features enabled or not')
    date_joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        is_new_user = False
        if not self.pk:
            is_new_user = True
        super().save(*args, **kwargs)
        if is_new_user:
            from pyPlants.models import NotificationCenter
            NotificationCenter.objects.create(user=self)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name

    def has_reached_max_ai_usage(self):
        max_usage = settings.MAX_OPEN_API_USAGE
        if self.is_staff:
            return False
        return self.current_ai_usage() >= max_usage

    def current_ai_usage(self):
        from ai.models import AIPlantAnswer
        return AIPlantAnswer.objects.filter(plant__user=self).count()
