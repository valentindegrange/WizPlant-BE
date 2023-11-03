from datetime import date, timedelta

from django.test import TestCase, tag
from freezegun import freeze_time

from pyPlants.constants import Seasons
from pyPlants.models import Plant, PlantUser


@tag('plant')
class PlantTest(TestCase):
    def setUp(self):
        self.user = PlantUser.objects.create_user(
            email='foo@bar.com'
        )
        self.plant_only_water = Plant.objects.create(
            name='Pachira',
            user=self.user,
            water_frequency_summer=7,
            water_frequency_winter=14
        )

    def test_water(self):
        self.plant_only_water.water()
        self.assertIsNotNone(self.plant_only_water.last_watered)

    def test_should_not_water(self):
        self.plant_only_water.water()
        self.assertFalse(self.plant_only_water.should_water())

    def test_should_water(self):
        self.assertTrue(self.plant_only_water.should_water())

    def test_should_water_summer(self):
        with freeze_time('2023-6-1'):
            self.plant_only_water.water()
        with freeze_time('2023-6-8'):
            self.assertTrue(self.plant_only_water.should_water())

    def test_should_water_winter(self):
        with freeze_time('2023-1-1'):
            self.plant_only_water.water()
        with freeze_time('2023-1-15'):
            self.assertTrue(self.plant_only_water.should_water())

    def test_not_should_water_summer(self):
        with freeze_time('2023-6-1'):
            self.plant_only_water.water()
        with freeze_time('2023-6-7'):
            self.assertFalse(self.plant_only_water.should_water())

    def test_not_should_water_winter(self):
        with freeze_time('2023-1-1'):
            self.plant_only_water.water()
        with freeze_time('2023-1-14'):
            self.assertFalse(self.plant_only_water.should_water())

    def test_next_water_date(self):
        # not watered yet
        with freeze_time('2023-1-1'):
            today = date.today()
            self.assertEqual(self.plant_only_water.next_water_date(), today)
        # water in winter
        with freeze_time('2023-1-1'):
            self.plant_only_water.water()
            dt = date.today() + timedelta(days=14)
            self.assertEqual(self.plant_only_water.next_water_date(), dt)
        # water in summer
        with freeze_time('2023-6-1'):
            self.plant_only_water.water()
            dt = date.today() + timedelta(days=7)
            self.assertEqual(self.plant_only_water.next_water_date(), dt)

    def test_fertilize(self):
        self.assertRaises(ValueError, self.plant_only_water.fertilize)
        self.plant_only_water.fertilizer = True
        self.plant_only_water.save()
        self.plant_only_water.fertilize()
        self.assertIsNotNone(self.plant_only_water.last_fertilized)

    @freeze_time('2023-12-20')
    def test_should_not_fertilize(self):
        # return False if not set
        self.assertFalse(self.plant_only_water.should_fertilize())
        # raises error if no season is defined
        self.plant_only_water.fertilizer = True
        self.plant_only_water.save()
        self.assertRaises(ValueError, self.plant_only_water.should_fertilize)
        # returns False if not in the right season
        self.plant_only_water.fertilizer_season = Seasons.WINTER
        self.plant_only_water.save()
        self.assertFalse(self.plant_only_water.should_fertilize())
        # returns False if in the right season but already fertilized
        self.plant_only_water.fertilizer_season = Seasons.AUTUMN
        self.plant_only_water.save()
        self.plant_only_water.fertilize()
        self.assertFalse(self.plant_only_water.should_fertilize())

    @freeze_time('2023-12-21')
    def test_should_fertilize(self):
        self.plant_only_water.fertilizer = True
        self.plant_only_water.fertilizer_season = Seasons.WINTER
        self.plant_only_water.save()
        self.assertTrue(self.plant_only_water.should_fertilize())

    def test_next_fertilize_date(self):
        # winter
        # fertilize in winter, during winter
        with freeze_time('2023-1-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.WINTER
            self.plant_only_water.save()
            dt = date(2022, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # fertilize in winter, after winter
        with freeze_time('2023-6-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.WINTER
            self.plant_only_water.save()
            dt = date(2023, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # fertilize in winter, before winter
        with freeze_time('2022-6-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.WINTER
            self.plant_only_water.save()
            dt = date(2022, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # summer
        # fertilize in summer, during summer
        with freeze_time('2023-7-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.SUMMER
            self.plant_only_water.save()
            dt = date(2023, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # fertilize in summer, before summer
        with freeze_time('2023-3-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.SUMMER
            self.plant_only_water.save()
            dt = date(2023, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # fertilize in summer, after summer
        with freeze_time('2023-10-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.SUMMER
            self.plant_only_water.save()
            dt = date(2024, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)

    def test_next_fertilize_date_after_fertilized(self):
        # winter
        # fertilize in winter, during winter
        with freeze_time('2023-1-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.WINTER
            self.plant_only_water.save()
            self.plant_only_water.fertilize()
            dt = date(2023, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # fertilize in winter, after winter
        with freeze_time('2023-6-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.WINTER
            self.plant_only_water.save()
            self.plant_only_water.fertilize()
            dt = date(2023, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # fertilize in winter, before winter
        with freeze_time('2022-6-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.WINTER
            self.plant_only_water.save()
            self.plant_only_water.fertilize()
            dt = date(2022, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # summer
        # fertilize in summer, during summer
        with freeze_time('2023-7-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.SUMMER
            self.plant_only_water.save()
            self.plant_only_water.fertilize()
            dt = date(2024, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # fertilize in summer, before summer
        with freeze_time('2023-3-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.SUMMER
            self.plant_only_water.save()
            self.plant_only_water.fertilize()
            dt = date(2023, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)
        # fertilize in summer, after summer
        with freeze_time('2023-10-1'):
            self.plant_only_water.fertilizer = True
            self.plant_only_water.fertilizer_season = Seasons.SUMMER
            self.plant_only_water.save()
            self.plant_only_water.fertilize()
            dt = date(2024, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_fertilize_date(), dt)

    def test_repot(self):
        self.assertRaises(ValueError, self.plant_only_water.repot)
        self.plant_only_water.repotting = True
        self.plant_only_water.save()
        self.plant_only_water.repot()
        self.assertIsNotNone(self.plant_only_water.last_repotted)

    @freeze_time('2023-12-20')
    def test_should_not_repot(self):
        # return False if not set
        self.assertFalse(self.plant_only_water.should_repot())
        # raises error if no season is defined
        self.plant_only_water.repotting = True
        self.plant_only_water.save()
        self.assertRaises(ValueError, self.plant_only_water.should_repot)
        # returns False if not in the right season
        self.plant_only_water.repotting_season = Seasons.WINTER
        self.plant_only_water.save()
        self.assertFalse(self.plant_only_water.should_repot())
        # returns False if in the right season but already fertilized
        self.plant_only_water.repotting_season = Seasons.AUTUMN
        self.plant_only_water.save()
        self.plant_only_water.repot()
        self.assertFalse(self.plant_only_water.should_repot())

    @freeze_time('2023-12-21')
    def test_should_repot(self):
        self.plant_only_water.repotting = True
        self.plant_only_water.repotting_season = Seasons.WINTER
        self.plant_only_water.save()
        self.assertTrue(self.plant_only_water.should_repot())

    def test_next_repotting_date(self):
        # winter
        # repot in winter, during winter
        with freeze_time('2023-1-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.WINTER
            self.plant_only_water.save()
            dt = date(2022, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # repot in winter, after winter
        with freeze_time('2023-6-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.WINTER
            self.plant_only_water.save()
            dt = date(2023, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # repot in winter, before winter
        with freeze_time('2022-6-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.WINTER
            self.plant_only_water.save()
            dt = date(2022, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # summer
        # repot in summer, during summer
        with freeze_time('2023-7-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.SUMMER
            self.plant_only_water.save()
            dt = date(2023, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # repot in summer, before summer
        with freeze_time('2023-3-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.SUMMER
            self.plant_only_water.save()
            dt = date(2023, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # repot in summer, after summer
        with freeze_time('2023-10-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.SUMMER
            self.plant_only_water.save()
            dt = date(2024, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)

    def test_next_repotting_date_after_repotted(self):
        # winter
        # repot in winter, during winter
        with freeze_time('2023-1-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.WINTER
            self.plant_only_water.save()
            self.plant_only_water.repot()
            dt = date(2023, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # repot in winter, after winter
        with freeze_time('2023-6-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.WINTER
            self.plant_only_water.save()
            self.plant_only_water.repot()
            dt = date(2023, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # repot in winter, before winter
        with freeze_time('2022-6-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.WINTER
            self.plant_only_water.save()
            self.plant_only_water.repot()
            dt = date(2022, 12, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # summer
        # repot in summer, during summer
        with freeze_time('2023-7-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.SUMMER
            self.plant_only_water.save()
            self.plant_only_water.repot()
            dt = date(2024, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # repot in summer, before summer
        with freeze_time('2023-3-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.SUMMER
            self.plant_only_water.save()
            self.plant_only_water.repot()
            dt = date(2023, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
        # repot in summer, after summer
        with freeze_time('2023-10-1'):
            self.plant_only_water.repotting = True
            self.plant_only_water.repotting_season = Seasons.SUMMER
            self.plant_only_water.save()
            self.plant_only_water.repot()
            dt = date(2024, 6, 21)
            self.assertEqual(self.plant_only_water.get_next_repotting_date(), dt)
