import datetime
from django.db.models import Q


def days_apart(start_date, end_date):
    """ Return the number of days apart between two datetimes

    >>> day1 = datetime.datetime(year=2011, month=9, day=29)
    >>> day2 = datetime.datetime(year=2011, month=10, day=3)
    >>> days_apart(day1, day2)
    4
    """
    return (end_date.date() - start_date.date()).days


def day_range(start_date, end_date):
    """ Given two dates, generate (date, day#) pairs for all the days in the
    range, inclusive

    >>> day1 = datetime.datetime(year=2011, month=9, day=29)
    >>> day2 = datetime.datetime(year=2011, month=10, day=3)
    >>> list(day_range(day1, day2))
    [(datetime.date(2011, 9, 29), 0), (datetime.date(2011, 9, 30), 1), (datetime.dat
    e(2011, 10, 1), 2), (datetime.date(2011, 10, 2), 3)]
    """
    for day in range(days_apart(start_date, end_date) + 1):
        date = start_date.date() + datetime.timedelta(days=day)
        yield date, day


def business_day_range(start_date, end_date):
    """ Given two dates, generate (date, day#) pairs for all the business days in
    the range, inclusive

    >>> day1 = datetime.datetime(year=2011, month=5, day=31)
    >>> day2 = datetime.datetime(year=2011, month=6, day=6)
    >>> list(business_day_range(day1, day2))
    [(datetime.date(2011, 5, 31), 0), (datetime.date(2011, 6, 1), 1),
    (datetime.date(2011, 6, 2), 2), (datetime.date(2011, 6, 3), 3)]
    """
    for date, day in day_range(start_date, end_date):
        if is_business_day(date):
            yield date, day


def days_of_work(issues):
    """Given a queryset of issues, return the number of days it is estimated
    to complete all of them."""
    return float(sum(i or 1 for i in issues.values_list('days_estimate', flat=True)))


def work_left(issues, date):
    """Given a queryset of issues, return how many days of work is
    estimated to complete all of them excluding completed issues on or before
    a given date"""
    one_day = datetime.timedelta(days=1)
    return days_of_work(issues.exclude(Q(close_date__isnull=True) | Q(close_date__gt=date + one_day)))


def is_business_day(date):
    return date.weekday() <= 4
