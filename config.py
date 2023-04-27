# BUILT-IN
import os
import datetime
import calendar

# LOCAL
from databases.neo4j_users import *


RANGES = {index: f'{num}:00-{num+2}:00' if len(str(num)) == 2 else f'0{num}:00-{num+2}:00'
          for index, num in enumerate(range(6, 22, 2))}
RANGES.update({
    8: '22:00-00:00',
    9: '00:00-02:00',
    10: '02:00-04:00'
})
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
