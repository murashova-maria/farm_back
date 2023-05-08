# LIBS
import os
import json
import logging
from queue import Queue

# LOCAL
from config import *
from databases.neo4j_users import *
from tmp_solutions.conv_tmp import JSONWriter
from farm.social_media.utils import QueuedTask
from databases.utils import get_exact_date, get_randomized_date
from databases.users import ConversationsPostgres, BaseDB, engine, sessionmaker

# OTHER
from sqlalchemy.exc import SQLAlchemyError

print('loader был импортирован. ')


def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


GOLOGIN_API_TOKEN = os.getenv('GOLOGIN_API_TOKEN')


main_queue = Queue()
IMG_DIR = f'{os.getcwd()}/images/'
DATE_FORMAT = '%d.%m.%Y %H:%M'
