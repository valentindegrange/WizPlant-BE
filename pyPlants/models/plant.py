from datetime import date, timedelta

from PIL import Image
from django.db import models
from django.db.models import When, Q, Value, Case, F

from pyPlants.constants import Seasons
from pyPlants.models import AbstractPlantModel, PlantUser
from pyPlants.season_manager import SeasonManager
from pyPlants.utils import plant_pics_directory_path


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

    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=plant_pics_directory_path, null=True, blank=True)
    user = models.ForeignKey(PlantUser, on_delete=models.CASCADE)

    # Sunlight
    sunlight = models.CharField(
        max_length=20,
        choices=SunlightOptions.choices,
        null=True,
        blank=True
    )
    sun_exposure = models.CharField(
        max_length=20,
        choices=SunExposureOptions.choices,
        null=True,
        blank=True
    )

    # Watering
    water_frequency_summer = models.IntegerField(null=True, blank=True)
    water_frequency_winter = models.IntegerField(null=True, blank=True)
    last_watered = models.DateField(null=True, blank=True)
    should_water = models.BooleanField(default=False)
    next_water_date = models.DateField(null=True, blank=True)

    leaf_mist = models.BooleanField(default=False)

    # fertilize
    fertilizer = models.BooleanField(default=False)
    fertilizer_season = models.CharField(
        max_length=20,
        choices=SeasonType.choices,
        blank=True,
        null=True,
    )
    last_fertilized = models.DateField(null=True, blank=True)
    should_fertilize = models.BooleanField(default=False)
    next_fertilize_date = models.DateField(null=True, blank=True)
    # repot
    repotting = models.BooleanField(default=False)
    repotting_season = models.CharField(
        max_length=20,
        choices=SeasonType.choices,
        blank=True,
        null=True,
    )
    last_repotted = models.DateField(null=True, blank=True)
    should_repot = models.BooleanField(default=False)
    next_repotting_date = models.DateField(null=True, blank=True)

    needs_care = models.GeneratedField(
        expression=Case(
            When(should_water=True, then=Value(True)),
            When(should_repot=True, then=Value(True)),
            When(should_fertilize=True, then=Value(True)),
            default=Value(False)),
        output_field=models.BooleanField(),
        db_persist=True
    )

    # other
    extra_tips = models.TextField(null=True, blank=True)

    is_complete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.is_complete = self.check_is_complete()
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 512 or img.width > 512:
                output_size = (512, 512)
                img.thumbnail(output_size)
                img.save(self.image.path)

    def check_is_complete(self):
        """Checks if all required fields are filled out."""
        is_complete = False
        if self.name and self.sunlight and self.sun_exposure and self.water_frequency_summer and self.water_frequency_winter:
            is_complete = True
        return is_complete

    def water(self):
        self.last_watered = date.today()
        self.save()
        self.refresh_from_db()
        self.get_should_water()

    def get_should_water(self):
        should_water = date.today() >= self.get_next_water_date()
        self.should_water = should_water
        self.save()
        return should_water

    def get_next_water_date(self):
        if self.last_watered is None:
            next_water_date = date.today()
        else:
            water_frequency = self.get_water_frequency()
            next_water_date = self.last_watered + timedelta(days=water_frequency)
        self.next_water_date = next_water_date
        self.save()
        return next_water_date

    def get_water_frequency(self):
        season_manager = SeasonManager()
        half_year_season = season_manager.get_half_year(date=self.last_watered)
        if half_year_season == Seasons.SUMMER:
            water_frequency = self.water_frequency_summer
        else:
            water_frequency = self.water_frequency_winter
        return water_frequency

    def fertilize(self):
        if self.fertilizer:
            self.last_fertilized = date.today()
            self.save()
            self.refresh_from_db()
            self.get_should_fertilize()
        else:
            raise ValueError("This plant does not require fertilizer.")

    def get_should_fertilize(self):
        """Should only be called once a day or when data needs to be refreshed"""
        should_fertilize = False
        if self.fertilizer:
            next_fertilize_date = self.get_next_fertilize_date()
            if next_fertilize_date:
                should_fertilize = date.today() >= next_fertilize_date
        self.should_fertilize = should_fertilize
        self.save()
        return should_fertilize

    def get_next_fertilize_date(self):
        """Should only be called once a day or when data needs to be refreshed"""
        next_fertilize_date = None
        if self.fertilizer:
            season_manager = SeasonManager()
            next_fertilize_date = season_manager.get_next_or_current_season_start_date(
                season=self.fertilizer_season, date=self.last_fertilized
            )
        self.next_fertilize_date = next_fertilize_date
        self.save()
        return next_fertilize_date

    def repot(self):
        if self.repotting:
            self.last_repotted = date.today()
            self.save()
            self.refresh_from_db()
            self.get_should_repot()
        else:
            raise ValueError("This plant does not require repotting.")

    def get_should_repot(self):
        """Should only be called once a day or when data needs to be refreshed"""
        should_repot = False
        if self.repotting:
            next_repot_date = self.get_next_repotting_date()
            if next_repot_date:
                should_repot = date.today() >= next_repot_date
        self.should_repot = should_repot
        self.save()
        return should_repot

    def get_next_repotting_date(self):
        """Should only be called once a day or when data needs to be refreshed"""
        next_repotting_date = None
        if self.repotting:
            season_manager = SeasonManager()
            next_repotting_date = season_manager.get_next_or_current_season_start_date(
                season=self.repotting_season, date=self.last_repotted
            )
        self.next_repotting_date = next_repotting_date
        self.save()
        return next_repotting_date
