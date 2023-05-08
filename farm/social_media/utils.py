# TWITTER API
import tweepy

# LOCAL
from loader import *

# OTHER
import re
import time


class QueuedTask:
    def __init__(self, obj, method, args: list | dict):
        self.obj = obj
        self.method = method
        self.args = args

    def __call__(self):
        try:
            if type(self.args) is dict:
                for key, value in self.args.items():
                    if value.get('type') != 'json':
                        continue
                    getattr(self.obj, self.method)(self.args)
                    return
        except Exception as ex:
            pass
        if type(self.args) is dict:
            self.args = {key: (value if value is not None else 'None') for key, value in self.args.items()}
            getattr(self.obj, self.method)(**self.args)
        else:
            self.args = [arg if arg is not None else 'None' for arg in self.args]
            getattr(self.obj, self.method)(*self.args)


def get_users_liked(api_id, api_hash, post_id: int):
    auth = tweepy.OAuth1UserHandler(api_id, api_hash)
    api = tweepy.API(auth)
    likes = api.get_favorites(id=post_id)
    return [{'name': user.name, 'screen_name': user.screen_name, 'user_id': user.user_id} for user in likes]


def replace_none(lst):
    for i, val in enumerate(lst):
        if isinstance(val, list):
            lst[i] = replace_none(val)
        elif val is None:
            lst[i] = 'None'
    return lst


def replace_none_dict(d: dict) -> dict:
    return {k: 'None' if v is None else v for k, v in d.items()}


if __name__ == '__main__':
    pass
