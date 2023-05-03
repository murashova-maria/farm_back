# LIBS
import os
import json
import logging
from queue import Queue

# LOCAL
from config import *
from databases.neo4j_users import *
from farm.social_media.utils import QueuedTask
from databases.utils import get_exact_date, get_randomized_date
from tmp_solutions.conv_tmp import HandleConversation, HandleConversationTest

# logging.basicConfig(
#     level=logging.DEBUG,
    # format='%(asctime)s %(levelname) %(message)s',
    # handlers=[logging.StreamHandler()]
# )


def read_json(filename='conversations.json'):
    with open(filename, 'r') as f:
        return json.load(f)


GOLOGIN_API_TOKEN = os.getenv('GOLOGIN_API_TOKEN')


main_queue = Queue()
IMG_DIR = f'{os.getcwd()}/images/'
DATE_FORMAT = '%d.%m.%Y %H:%M'
