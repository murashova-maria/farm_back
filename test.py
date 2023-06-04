# OTHER
import os
import json
from time import sleep
from pprint import pprint

# LOCAL
from loader import UserBase, FacebookProfileBase, InstagramProfileBase, \
    KeywordBase, TwitterProfileBase, SelfPostsBase, session, ConversationDB


def add_old_bots():
    exist = []
    for usr in UserBase().get_all():
        sleep(0.5)
        username = usr.get('username')
        password = usr.get('password')
        phone_number = usr.get('phone_number')
        network = usr.get('social_media')
        gologin_id = usr.get('gologin_id')
        auth_code = usr.get('auth_code')
        if gologin_id in exist:
            print(gologin_id)
        exist.append(gologin_id)
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
        print()


if __name__ == '__main__':
    for key, value in ConversationDB.get_all_conversations().items():
        pprint({key: value})
    a = int(input('Add old bots - 1, clean database - 0: '))
    if a:
        add_old_bots()
    else:
        tables = [UserBase, FacebookProfileBase, InstagramProfileBase, KeywordBase, TwitterProfileBase, SelfPostsBase]
        for table in tables:
            for elem in session.query(table).all():
                session.delete(elem)
            session.commit()
