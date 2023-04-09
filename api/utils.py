# LOCAL
from loader import DATE_FORMAT

# DATE
from datetime import datetime


def ready_to_post(date: str):
    if date == 'now':
        return True
    datetime_format = datetime.strptime(date, DATE_FORMAT)
    return datetime_format <= datetime.now()


if __name__ == '__main__':
    pass
