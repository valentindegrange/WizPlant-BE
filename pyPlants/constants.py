class Seasons:
    SPRING = 'Spring'
    SUMMER = 'Summer'
    AUTUMN = 'Autumn'
    WINTER = 'Winter'

    def __getitem__(self, item):
        return getattr(self, item)


class Notifications:
    EMAIL = 'EMAIL'
    SMS = 'SMS'
    IN_APP = 'IN_APP'



