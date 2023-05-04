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
from databases.users import ConversationsPostgres, BaseDB, engine, sessionmaker

# OTHER
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, wait_fixed, stop_after_attempt


@retry(wait=wait_fixed(2), stop=stop_after_attempt(5), reraise=True)
def safe_commit(session):
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e


def read_json(filename='conversations.json'):
    with open(filename, 'r') as f:
        return json.load(f)


GOLOGIN_API_TOKEN = os.getenv('GOLOGIN_API_TOKEN')


if 'bots_farm.db' not in os.listdir():
    BaseDB.metadata.create_all(engine)
user_session = sessionmaker(bind=engine)
user_session = user_session()
main_queue = Queue()
IMG_DIR = f'{os.getcwd()}/images/'
DATE_FORMAT = '%d.%m.%Y %H:%M'
