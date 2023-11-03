from datetime import date

from django.test import TestCase, tag
from pyPlants.season_manager import SeasonManager
from pyPlants.constants import Seasons


@tag('season-manager')
class SeasonManagerTest(TestCase):

    def setUp(self):
        self.season_manager = SeasonManager()

    def test_get_season(self):
        season_manager = self.season_manager
        # regular dates
        self.assertEqual(season_manager.get_season(date=date(2023, 1, 1)), Seasons.WINTER)
        self.assertEqual(season_manager.get_season(date=date(2023, 2, 1)), Seasons.WINTER)
        self.assertEqual(season_manager.get_season(date=date(2023, 3, 1)), Seasons.WINTER)
        self.assertEqual(season_manager.get_season(date=date(2023, 4, 1)), Seasons.SPRING)
        self.assertEqual(season_manager.get_season(date=date(2023, 5, 1)), Seasons.SPRING)
        self.assertEqual(season_manager.get_season(date=date(2023, 6, 1)), Seasons.SPRING)
        self.assertEqual(season_manager.get_season(date=date(2023, 7, 1)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_season(date=date(2023, 8, 1)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_season(date=date(2023, 9, 1)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_season(date=date(2023, 10, 1)), Seasons.AUTUMN)
        self.assertEqual(season_manager.get_season(date=date(2023, 11, 1)), Seasons.AUTUMN)
        self.assertEqual(season_manager.get_season(date=date(2023, 12, 1)), Seasons.AUTUMN)
        self.assertEqual(season_manager.get_season(date=date(2023, 12, 31)), Seasons.WINTER)

        # edges
        self.assertEqual(season_manager.get_season(date=date(2023, 3, 20)), Seasons.SPRING)
        self.assertEqual(season_manager.get_season(date=date(2023, 6, 20)), Seasons.SPRING)
        self.assertEqual(season_manager.get_season(date=date(2023, 6, 21)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_season(date=date(2023, 9, 21)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_season(date=date(2023, 9, 22)), Seasons.AUTUMN)
        self.assertEqual(season_manager.get_season(date=date(2023, 12, 20)), Seasons.AUTUMN)
        self.assertEqual(season_manager.get_season(date=date(2023, 12, 21)), Seasons.WINTER)
        self.assertEqual(season_manager.get_season(date=date(2023, 3, 19)), Seasons.WINTER)

    def test_get_half_year(self):
        season_manager = self.season_manager
        # regular dates
        self.assertEqual(season_manager.get_half_year(date=date(2023, 1, 1)), Seasons.WINTER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 2, 1)), Seasons.WINTER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 3, 1)), Seasons.WINTER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 4, 1)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 5, 1)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 6, 1)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 7, 1)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 8, 1)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 9, 1)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 10, 1)), Seasons.WINTER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 11, 1)), Seasons.WINTER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 12, 1)), Seasons.WINTER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 12, 31)), Seasons.WINTER)

        # edges
        self.assertEqual(season_manager.get_half_year(date=date(2023, 3, 20)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 6, 20)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 6, 21)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 9, 21)), Seasons.SUMMER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 9, 22)), Seasons.WINTER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 12, 20)), Seasons.WINTER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 12, 21)), Seasons.WINTER)
        self.assertEqual(season_manager.get_half_year(date=date(2023, 3, 19)), Seasons.WINTER)

    def test_date_in_season(self):
        season_manager = self.season_manager
        self.assertTrue(season_manager.date_in_season(date=date(2023, 3, 20), season=Seasons.SPRING))
        self.assertTrue(season_manager.date_in_season(date=date(2023, 6, 20), season=Seasons.SPRING))
        self.assertTrue(season_manager.date_in_season(date=date(2023, 6, 21), season=Seasons.SUMMER))
        self.assertTrue(season_manager.date_in_season(date=date(2023, 9, 21), season=Seasons.SUMMER))
        self.assertTrue(season_manager.date_in_season(date=date(2023, 9, 22), season=Seasons.AUTUMN))
        self.assertTrue(season_manager.date_in_season(date=date(2023, 12, 20), season=Seasons.AUTUMN))
        self.assertTrue(season_manager.date_in_season(date=date(2023, 12, 21), season=Seasons.WINTER))
        self.assertTrue(season_manager.date_in_season(date=date(2023, 3, 19), season=Seasons.WINTER))
        # error case
        self.assertRaises(ValueError, season_manager.date_in_season, date=date(2023, 3, 19), season='foo')

    def test_get_start_date_of_current_or_next_seasons(self):
        season_manager = self.season_manager
        # winter case
        self.assertEqual(
            season_manager.get_start_date_of_current_or_next_seasons(date=date(2023, 1, 1), season=Seasons.WINTER),
            date(2022, 12, 21)
        )
        self.assertEqual(
            season_manager.get_start_date_of_current_or_next_seasons(date=date(2023, 12, 20), season=Seasons.WINTER),
            date(2023, 12, 21)
        )
        self.assertEqual(
            season_manager.get_start_date_of_current_or_next_seasons(date=date(2023, 12, 21), season=Seasons.WINTER),
            date(2023, 12, 21)
        )
        # other seasons
        self.assertEqual(
            season_manager.get_start_date_of_current_or_next_seasons(date=date(2023, 3, 20), season=Seasons.SPRING),
            date(2023, 3, 20)
        )
        self.assertEqual(
            season_manager.get_start_date_of_current_or_next_seasons(date=date(2023, 5, 20), season=Seasons.SPRING),
            date(2023, 3, 20)
        )
        self.assertEqual(
            season_manager.get_start_date_of_current_or_next_seasons(date=date(2023, 7, 20), season=Seasons.SPRING),
            date(2024, 3, 20)
        )
        self.assertEqual(
            season_manager.get_start_date_of_current_or_next_seasons(date=date(2024, 3, 19), season=Seasons.SPRING),
            date(2024, 3, 20)
        )
        # error case
        self.assertRaises(ValueError, season_manager.get_start_date_of_current_or_next_seasons, date=date(2023, 3, 19), season='foo')

    def test_get_start_date_of_target_season(self):
        season_manager = self.season_manager
        # basic case
        self.assertEqual(
            season_manager.get_start_date_of_target_season(date=date(2023, 2, 20), season=Seasons.SPRING),
            date(2023, 3, 20)
        )
        self.assertEqual(
            season_manager.get_start_date_of_target_season(date=date(2023, 3, 20), season=Seasons.SPRING),
            date(2024, 3, 20)
        )
        self.assertEqual(
            season_manager.get_start_date_of_target_season(date=date(2023, 4, 1), season=Seasons.SPRING),
            date(2024, 3, 20)
        )
        self.assertEqual(
            season_manager.get_start_date_of_target_season(date=date(2023, 7, 1), season=Seasons.SPRING),
            date(2024, 3, 20)
        )
        # winter case
        self.assertEqual(
            season_manager.get_start_date_of_target_season(date=date(2022, 12, 25), season=Seasons.WINTER),
            date(2023, 12, 21)
        )
        self.assertEqual(
            season_manager.get_start_date_of_target_season(date=date(2023, 2, 20), season=Seasons.WINTER),
            date(2023, 12, 21)
        )
        self.assertEqual(
            season_manager.get_start_date_of_target_season(date=date(2023, 12, 20), season=Seasons.WINTER),
            date(2023, 12, 21)
        )
        # error case
        self.assertRaises(ValueError, season_manager.get_start_date_of_target_season, date=date(2023, 3, 19), season='foo')
