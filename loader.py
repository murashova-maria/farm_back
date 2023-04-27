# LIBS
import os
import logging
from queue import Queue

# LOCAL
from config import *
from databases.neo4j_users import *
from farm.social_media.utils import QueuedTask
from databases.utils import get_exact_date, get_randomized_date

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s %(levelname) %(message)s',
#     handlers=[logging.StreamHandler()]
# )

GOLOGIN_API_TOKEN = os.getenv('GOLOGIN_API_TOKEN')


main_queue = Queue()
IMG_DIR = f'{os.getcwd()}/images/'
DATE_FORMAT = '%d.%m.%Y %H:%M'
