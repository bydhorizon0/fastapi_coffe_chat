from datetime import date, timedelta


def get_start_weekday_of_month(year: int, month: int) -> int:
    """
    월의 시작 요일을 가져옴(월요일=0, 일요일=6)
    :param year:
    :param month:
    :return:
    """
    result = date(year, month, 1)
    return result.weekday()


def get_last_day_of_month(year: int, month: int) -> int:
    """
    월의 마지막 날짜를 가져옴
    :param year:
    :param month:
    :return:
    """
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    result = next_month - timedelta(days=1)
    return result.day


def get_range_days_of_month(year: int, month: int):
    """
    월의 일수를 가져옴
    :param year:
    :param month:
    :return:
    """
    # 월의 시작 요일을 가져옴 (월요일=0, 일요일=6)
    start_weekday = get_start_weekday_of_month(year, month)

    # 월의 마지막 날짜를 가져옴
    last_day = get_last_day_of_month(year, month)

    # 월요일 0을 월요일 1로 변환(일요일=0으로 만들기 위해)
    start_weekday = (start_weekday + 1) % 7

    # 결과 리스트 생성
    result = [0] * start_weekday  # 시작 요일 전까지 0으로 채움

    return result + list(range(1, last_day + 1))
