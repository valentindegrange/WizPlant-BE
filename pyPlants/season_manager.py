import datetime
import logging

from .constants import Seasons


logger = logging.getLogger(__name__)


class SeasonManager:
    def __init__(self):
        self.seasons = {
            Seasons.SPRING: dict(start=(3, 20), end=(6, 20)),
            Seasons.SUMMER: dict(start=(6, 21), end=(9, 21)),
            Seasons.AUTUMN: dict(start=(9, 22), end=(12, 20)),
            Seasons.WINTER: dict(start=(12, 21), end=(3, 19))
        }
        self.half_years = {
            Seasons.SPRING: Seasons.SUMMER,
            Seasons.SUMMER: Seasons.SUMMER,
            Seasons.AUTUMN: Seasons.WINTER,
            Seasons.WINTER: Seasons.WINTER
        }

    def get_season(self, date: datetime.date):
        """Returns the season for a given date"""
        for season, dates in self.seasons.items():
            if self.date_in_season(date, season):
                return season

    def get_half_year(self, date):
        """Returns the half year season (WINTER or SUMMER) for a given date"""
        return self.half_years[self.get_season(date)]

    def date_in_season(self, date: datetime.date, season):
        """Returns True if the date is in the given season"""
        if season not in self.seasons:
            raise ValueError("Invalid season")
        start = self.seasons[season]['start']
        end = self.seasons[season]['end']
        # Handle seasons that do not cross the year boundary
        if start[0] < end[0] or (start[0] == end[0] and start[1] < end[1]):
            return (start[0], start[1]) <= (date.month, date.day) <= (end[0], end[1])
        # Handle seasons that cross the year boundary
        else:
            return (start[0], start[1]) <= (date.month, date.day) or (date.month, date.day) <= (end[0], end[1])

    def get_start_date_of_current_or_next_seasons(self, date: datetime.date, season):
        """Given a date and a season, returns the start date of the season (current or next)"""
        if season not in self.seasons:
            raise ValueError("Invalid season")
        current_year = date.year
        start_month, start_day = self.seasons[season]['start']
        end_month, end_day = self.seasons[season]['end']
        if season == Seasons.WINTER:
            season_start_date = datetime.date(current_year - 1, start_month, start_day)
            season_end_date = datetime.date(current_year, end_month, end_day)
            next_season_start_date = datetime.date(current_year, start_month, start_day)
        else:
            season_start_date = datetime.date(current_year, start_month, start_day)
            season_end_date = datetime.date(current_year, end_month, end_day)
            next_season_start_date = datetime.date(current_year + 1, start_month, start_day)
        if season_start_date <= date <= season_end_date:
            return season_start_date
        if date < season_start_date:
            return season_start_date
        if date > season_end_date:
            return next_season_start_date

    def get_start_date_of_target_season(self, date: datetime.date, season):
        """
        Given a date and a target season, returns the start date of the target season
        in the current or next year.
        """
        if season not in self.seasons:
            raise ValueError("Invalid season")
        start_month, start_day = self.seasons[season]['start']
        end_month, end_day = self.seasons[season]['end']

        # Handling the case for seasons that don't cross the year boundary
        if start_month < end_month or (start_month == end_month and start_day < end_day):
            if (date.month < start_month) or (date.month == start_month and date.day < start_day):
                return datetime.date(date.year, start_month, start_day)
            else:
                return datetime.date(date.year + 1, start_month, start_day)

        # Handling the case for seasons that cross the year boundary (e.g., Winter)
        if (date.month < start_month) or (date.month == start_month and date.day < start_day):
            return datetime.date(date.year, start_month, start_day)
        elif (date.month > end_month) or (date.month == end_month and date.day > end_day):
            return datetime.date(date.year + 1, start_month, start_day)
        else:
            # If the date is in the season, but we are targeting the next occurrence
            return datetime.date(date.year + 1, start_month, start_day)

    def get_current_season(self):
        """Returns the current season"""
        return self.get_season(datetime.date.today())

    def get_current_date_in_season(self, season):
        """Returns whether the current date is in the given season"""
        return self.date_in_season(datetime.date.today(), season)

    def get_next_or_current_season_start_date(self, season, date=None):
        """Returns the start date of the current or next season"""
        if date is None:
            return self.get_start_date_of_current_or_next_seasons(datetime.date.today(), season)
        else:
            return self.get_start_date_of_target_season(date, season)

    def get_current_half_year(self):
        """Returns the current half year"""
        return self.half_years[self.get_current_season()]
