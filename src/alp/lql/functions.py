# vim:fileencoding=utf8

__all__ = ['count']

def count(field, iterable):
    """
    Modifies iterable inplace by adding ``COUNT(field)`` column to all dicts within
    """
    for row in iterable:
        row['COUNT({0})'.format(field)] = len(row['__groups__'])

def percent(field, iterable):
    """
    Modifies iterable inplace by adding ``PERCENT(field)`` column to all dicts
    within. Depends on ``count()``.
    """
    count(field, iterable)
    total = float(sum(row['COUNT({0})'.format(field)] for row in iterable))
    for row in iterable:
        percent = row['COUNT({0})'.format(field)] / total
        row['PERCENT({0})'.format(field)] = "{0:0>6.2%}".format(percent)

def qps(field, iterable):
    """
        To provide Queries Per Second we need two hacks:
        Cause we have Scheme-less data base we need to parse each time on the
        fly. So we assume that there is field called TIME and it has date/time
        in provided format
    """
    pass
