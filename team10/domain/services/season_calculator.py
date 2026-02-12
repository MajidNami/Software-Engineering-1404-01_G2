from datetime import datetime
from ..enums.season import Season


def calculate_season_iran(date: datetime) -> Season:
    """Calculate the season in Iran based on a Gregorian date.

    Iran seasons (approximate Gregorian boundaries):
        Spring (Bahar):    March 20 - June 20
        Summer (Tabestan):  June 21 - September 22
        Autumn (Paeez):    September 23 - December 21
        Winter (Zemestan): December 22 - March 19
    """
    month = date.month
    day = date.day

    if (month == 3 and day >= 20) or month in (4, 5) or (month == 6 and day <= 20):
        return Season.SPRING
    elif (month == 6 and day >= 21) or month in (7, 8) or (month == 9 and day <= 22):
        return Season.SUMMER
    elif (month == 9 and day >= 23) or month in (10, 11) or (month == 12 and day <= 21):
        return Season.AUTUMN
    else:
        return Season.WINTER
