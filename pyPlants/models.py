from datetime import datetime, date, timedelta

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import User, PermissionsMixin
from django.db import models
from django.utils import timezone
from logging import getLogger

from pyPlants.constants import Seasons, Notifications
from pyPlants.season_manager import SeasonManager
from pyPlants.task_scheduler import schedule_check_plant_task

logger = getLogger(__name__)


class AbstractPlantModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # Your custom logic here
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class SeasonType(models.TextChoices):
    SPRING = Seasons.SPRING, Seasons.SPRING
    SUMMER = Seasons.SUMMER, Seasons.SUMMER
    AUTUMN = Seasons.AUTUMN, Seasons.AUTUMN
    WINTER = Seasons.WINTER, Seasons.WINTER


class Plant(AbstractPlantModel):
    class EarthMoistureOptions(models.TextChoices):
        LIGHTLY_DRY = 'LIGHTLY_DRY', 'Lightly Dry'
        DRY = 'DRY', 'Dry'
        VERY_DRY = 'VERY_DRY', 'Very Dry'

    class SunlightOptions(models.TextChoices):
        LIGHT_EXPOSURE = 'LIGHT_EXPOSURE', 'Light Exposure'
        PARTIAL_SHADE = 'PARTIAL_SHADE', 'Partial Shade'
        SHADE = 'SHADE', 'Shade'

    class SunExposureOptions(models.TextChoices):
        DIRECT_SUN = 'DIRECT_SUN', 'Direct Sun'
        NO_DIRECT_SUN = 'NO_DIRECT_SUN', 'No Direct Sun'

    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    user = models.ForeignKey(PlantUser, on_delete=models.CASCADE)

    # Sunlight
    sunlight = models.CharField(
        max_length=20,
        choices=SunlightOptions.choices,
        default=SunlightOptions.LIGHT_EXPOSURE,
    )
    sun_exposure = models.CharField(
        max_length=20,
        choices=SunExposureOptions.choices,
        default=SunExposureOptions.DIRECT_SUN,
    )

    # Watering
    water_frequency_summer = models.IntegerField()
    water_frequency_winter = models.IntegerField()
    last_watered = models.DateField(null=True, blank=True)
    leaf_mist = models.BooleanField(default=False)

    # Soil
    fertilizer = models.BooleanField(default=False)
    fertilizer_season = models.CharField(
        max_length=20,
        choices=SeasonType.choices,
        blank=True,
        null=True,
    )
    last_fertilized = models.DateField(null=True, blank=True)
    repotting = models.BooleanField(default=False)
    repotting_season = models.CharField(
        max_length=20,
        choices=SeasonType.choices,
        blank=True,
        null=True,
    )
    last_repotted = models.DateField(null=True, blank=True)

    # other
    extra_tips = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def water(self):
        self.last_watered = date.today()
        self.save()

    def should_water(self):
        if self.last_watered is None:
            return True
        else:
            return date.today() >= self.next_water_date()

    def next_water_date(self):
        if self.last_watered is None:
            return date.today()
        else:
            season_manager = SeasonManager()
            half_year_season = season_manager.get_half_year(date=self.last_watered)
            if half_year_season == Seasons.SUMMER:
                water_frequency = self.water_frequency_summer
            else:
                water_frequency = self.water_frequency_winter
            return self.last_watered + timedelta(days=water_frequency)

    def fertilize(self):
        if self.fertilizer:
            self.last_fertilized = date.today()
            self.save()
        else:
            raise ValueError("This plant does not require fertilizer.")

    def should_fertilize(self):
        if self.fertilizer:
            next_fertilize_date = self.get_next_fertilize_date()
            if next_fertilize_date:
                return date.today() >= next_fertilize_date
        return False

    def get_next_fertilize_date(self):
        if self.fertilizer:
            season_manager = SeasonManager()
            return season_manager.get_next_or_current_season_start_date(
                season=self.fertilizer_season, date=self.last_fertilized
            )
        return None

    def repot(self):
        if self.repotting:
            self.last_repotted = date.today()
            self.save()
        else:
            raise ValueError("This plant does not require repotting.")

    def should_repot(self):
        if self.repotting:
            next_repot_date = self.get_next_repotting_date()
            if next_repot_date:
                return date.today() >= next_repot_date
        return False

    def get_next_repotting_date(self):
        if self.repotting:
            season_manager = SeasonManager()
            return season_manager.get_next_or_current_season_start_date(
                season=self.repotting_season, date=self.last_repotted
            )
        return None


class NotificationType(models.TextChoices):
    EMAIL = Notifications.EMAIL, Notifications.EMAIL
    SMS = Notifications.SMS, Notifications.SMS
    IN_APP = Notifications.IN_APP, Notifications.IN_APP


class Notification(AbstractPlantModel):
    user = models.ForeignKey(PlantUser, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.IN_APP,
    )
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} - {self.notification_type} - {self.message}'

    def mark_as_viewed(self):
        self.viewed = True
        self.viewed_at = timezone.now()
        self.save()

    def mark_as_sent(self):
        self.sent = True
        self.sent_at = timezone.now()
        self.save()
        NotificationCenter.objects.filter(user=self.user).update(last_notification_sent=timezone.now())


class NotificationCenter(AbstractPlantModel):
    user = models.OneToOneField(PlantUser, on_delete=models.CASCADE)
    enable_in_app_notifications = models.BooleanField(default=True)
    enable_email_notifications = models.BooleanField(default=False)
    enable_sms_notifications = models.BooleanField(default=False)
    preferred_notification_hour = models.IntegerField(default=9)
    last_notification_sent = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        schedule_check_plant_task(self)
        super().save(*args, **kwargs)
