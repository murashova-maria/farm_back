# OTHER
import random
import datetime


def get_exact_date(day_of_week: int):
    today = datetime.date.today()
    days_until_day_of_week = (day_of_week - today.weekday()) % 7  # вычисляем количество дней до заданного дня недели
    nearest_date = today + datetime.timedelta(days=days_until_day_of_week)  # вычисляем ближайшую дату
    return nearest_date.strftime('%d.%m.%Y')


def get_randomized_date(day_of_week: int | str, time_range: str):
    nearest_date = get_exact_date(int(day_of_week))
    first_part, second_part = time_range.split('-')
    start_date = datetime.time(int(first_part.split(':')[0]), 0, 0)
    end_date = datetime.time(int(second_part.split(':')[0]), 0, 0)
    time_range = datetime.datetime.combine(datetime.date.today(), end_date) - datetime.datetime.combine(
        datetime.date.today(), start_date)  # вычисляем длительность временного промежутка

    random_time = datetime.datetime.combine(datetime.date.today(), start_date) + datetime.timedelta(
        seconds=random.randrange(time_range.seconds))
    return (datetime.datetime.strptime(f"{nearest_date} {random_time.strftime('%H:%M')}",
                                       '%d.%m.%Y %H:%M')).strftime('%d.%m.%Y %H:%M')
