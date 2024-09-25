import re


from delorean import Delorean, parse


from backend.constants import LOCAL_TZ


datetime_regex = re.compile(
    r'(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])')


def validate_datetime_str(s: str):
    return datetime_regex.match(s)


def parse_time(s: str, tz=LOCAL_TZ) -> Delorean:
    """
    處理時間字串，轉為 Delorean 時間物件
    :param s: 時間字串
    :param tz: 時區
    :return: Delorean
    """
    if validate_datetime_str(s):
        return parse(s, dayfirst=False, yearfirst=True, timezone=tz)



