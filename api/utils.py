# LOCAL
from loader import DATE_FORMAT

# DATE
from datetime import datetime


def ready_to_post(date):
    if date == 'now':
        return True
    if type(date) is str:
        date = datetime.strptime(date, DATE_FORMAT)
    return date <= datetime.now()


if __name__ == '__main__':
    pass
