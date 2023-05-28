# OTHER
import os
import json
from time import sleep

# LOCAL
from loader import UserBase


if __name__ == '__main__':
    for usr in UserBase().get_all():
        username = usr.get('username')
        password = usr.get('password')
        phone_number = usr.get('phone_number')
        network = usr.get('social_media')
        gologin_id = usr.get('gologin_id')
        auth_code = usr.get('auth_code')
        data = {
            "username": username,
            "password": password,
            "phone_number": phone_number,
            "network": network,
            "gologin_profile_id": gologin_id,
            'auth_code': auth_code,
        }

        request = f'curl -X POST -H "Content-Type: application/json" -d \'{json.dumps(data)}\' ' \
                  f'http://65.109.34.120:8080/bots/new/'
        os.system(request)
    pass
