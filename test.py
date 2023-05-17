# OTHER
from time import sleep

# LOCAL
from loader import *


if __name__ == '__main__':
    for usr in UserBase().get_all():
        print(usr if usr.get('phone_number').startswith('lidiyarod586@mail.ru') else None)
    pass
