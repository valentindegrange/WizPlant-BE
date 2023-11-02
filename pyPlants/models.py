from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Plant(models.Model):
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

    class FertilizerSeasonOptions(models.TextChoices):
        AUTUMN = 'AUTUMN', 'Autumn'
        SPRING = 'SPRING', 'Spring'

    class RepottingSeasonOptions(models.TextChoices):
        AUTUMN = 'AUTUMN', 'Autumn'
        SPRING = 'SPRING', 'Spring'

    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

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
    last_watered = models.DateTimeField(null=True, blank=True)
    leaf_mist = models.BooleanField(default=False)

    # Soil
    fertilizer = models.BooleanField(default=False)
    fertilizer_season = models.CharField(
        max_length=20,
        choices=FertilizerSeasonOptions.choices,
        blank=True,
        null=True,
    )
    last_fertilized = models.DateTimeField(null=True, blank=True)
    repotting = models.BooleanField(default=False)
    repotting_season = models.CharField(
        max_length=20,
        choices=RepottingSeasonOptions.choices,
        blank=True,
        null=True,
    )
    last_repotted = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def water(self):
        self.last_watered = timezone.now()
        self.save()

    def fertilize(self):
        if self.fertilizer:
            self.last_fertilized = timezone.now()
            self.save()
        else:
            raise ValueError("This plant does not require fertilizer.")

    def repot(self):
        if self.repotting:
            self.last_repotted = timezone.now()
            self.save()
        else:
            raise ValueError("This plant does not require repotting.")


class NotificationCenter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enable_email_notifications = models.BooleanField(default=False)
    enable_sms_notifications = models.BooleanField(default=False)
    preferred_notification_hour = models.IntegerField(default=9)
    last_notification_sent = models.DateTimeField(null=True, blank=True)
