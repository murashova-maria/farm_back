# OTHER
import os
import json
from time import sleep

# LOCAL
from loader import UserBase, FacebookProfileBase, InstagramProfileBase, \
    KeywordBase, TwitterProfileBase, SelfPostsBase, session


def add_old_bots():
    exist = []
    for usr in UserBase().get_all():
        sleep(0.5)
        username = usr.get('username')
        password = usr.get('password')
        phone_number = usr.get('phone_number')
        network = usr.get('social_media')
        gologin_id = usr.get('gologin_id')
        if gologin_id in exist:
            print(gologin_id)
        exist.append(gologin_id)
        data = {
            "username": username,
            "password": password,
            "phone_number": phone_number,
            "network": network,
            "gologin_profile_id": gologin_id
        }

        request = f'curl -X POST -H "Content-Type: application/json" -d \'{json.dumps(data)}\' ' \
                  f'http://65.109.34.120:8080/bots/new/'
        os.system(request)
        print()


if __name__ == '__main__':
    a = int(input('Add old bots - 0, clean database - 1'))
    if a:
        add_old_bots()
    else:
        tables = [UserBase, FacebookProfileBase, InstagramProfileBase, KeywordBase, TwitterProfileBase, SelfPostsBase]
        for table in tables:
            for elem in session.query(table).all():
                session.delete(elem)
            session.commit()
