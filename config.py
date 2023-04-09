# BUILT-IN
import os

# LOCAL
from databases.neo4j_users import *


uri = os.getenv('SERVER_NEO4J')
db_username = os.getenv('LOGIN_NEO4J')
db_password = os.getenv('PASSWORD_NEO4J')
local_graph = Graph(uri, auth=(db_username, db_password))

UserDB = User(local_graph)
TwitterProfileDB = TwitterProfile(local_graph)
FacebookProfileDB = FacebookProfile(local_graph)
FeedDB = Feed(local_graph)
SelfPostsDB = SelfPosts(local_graph)
