# BUILT-IN
import os
import datetime
from decouple import config

# LOCAL
from databases.neo4j_users import *
from databases.users_test import *


RANGES = {index: f'{num}:00-{num+2}:00' if len(str(num)) == 2 else f'0{num}:00-{num+2}:00'
          for index, num in enumerate(range(6, 22, 2))}
RANGES.update({
    8: '22:00-00:00',
    9: '00:00-02:00',
    10: '02:00-04:00'
})
uri = config('SERVER_NEO4J')
db_username = config('LOGIN_NEO4J')
db_password = config('PASSWORD_NEO4J')
local_graph = Graph(uri, auth=(db_username, db_password), secure=True)

# NEO4J
FeedDB = Feed(local_graph)

# SQLALCHEMY
UserDB = UserBase()
KeywordDB = KeywordBase()
ScheduleDB = ScheduleBase()
SelfPostsDB = SelfPostsBase()
TwitterProfileDB = TwitterProfileBase()
FacebookProfileDB = FacebookProfileBase()
InstagramProfileDB = InstagramProfileBase()
# UserDB = User(local_graph)
# ScheduleDB = Schedule(local_graph)
# KeywordDB = Keyword(local_graph)
# SelfPostsDB = SelfPosts(local_graph)
# TwitterProfileDB = TwitterProfile(local_graph)
# FacebookProfileDB = FacebookProfile(local_graph)
# InstagramProfileDB = InstagramProfile(local_graph)
