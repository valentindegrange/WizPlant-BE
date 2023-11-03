from datetime import datetime, date, timedelta

from django.contrib.auth.models import User
from django.db import models

from .constants import Seasons
from .season_manager import SeasonManager


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
    last_watered = models.DateField(null=True, blank=True)
    leaf_mist = models.BooleanField(default=False)

    # Soil
    fertilizer = models.BooleanField(default=False)
    fertilizer_season = models.CharField(
        max_length=20,
        choices=Seasons.spring_autumn_choices,
        blank=True,
        null=True,
    )
    last_fertilized = models.DateField(null=True, blank=True)
    repotting = models.BooleanField(default=False)
    repotting_season = models.CharField(
        max_length=20,
        choices=Seasons.spring_autumn_choices,
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
            next_repot_date = self.next_repot_date()
            if next_repot_date:
                return date.today() >= next_repot_date
        return False

    def next_repot_date(self):
        if self.repotting:
            season_manager = SeasonManager()
            return season_manager.get_next_or_current_season_start_date(
                season=self.repotting_season, date=self.last_repotted
            )
        return None


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)
    viewed = models.BooleanField(default=False)

    def mark_as_viewed(self):
        self.viewed = True
        self.save()


class NotificationCenter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enable_email_notifications = models.BooleanField(default=False)
    enable_sms_notifications = models.BooleanField(default=False)
    preferred_notification_hour = models.IntegerField(default=9)
    last_notification_sent = models.DateField(null=True, blank=True)

    def send_message(self, message):
        # very simple implementation for now
        print('New notification!')
        notification = Notification.objects.create(user=self.user, message=message)
        print(f'({notification.user.username}) {notification.date}: {notification.message}')
        self.last_notification_sent = date.today()
        self.save()
