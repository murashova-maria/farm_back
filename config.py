# BUILT-IN
import os
import datetime
import calendar

# LOCAL
from databases.neo4j_users import *


def current_day():
    return datetime.datetime.today().strftime('%A')


SCHEDULE_DAYS = calendar.day_name
uri = os.getenv('SERVER_NEO4J')
db_username = os.getenv('LOGIN_NEO4J')
db_password = os.getenv('PASSWORD_NEO4J')
local_graph = Graph(uri, auth=(db_username, db_password))

UserDB = User(local_graph)
TwitterProfileDB = TwitterProfile(local_graph)
FacebookProfileDB = FacebookProfile(local_graph)
InstagramProfileDB = InstagramProfile(local_graph)
KeywordDB = Keyword(local_graph)
FeedDB = Feed(local_graph)
SelfPostsDB = SelfPosts(local_graph)
ScheduleDB = Schedule(local_graph)
