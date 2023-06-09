from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, TIMESTAMP, FLOAT

engine = create_engine('sqlite:///bots_farm.db')
BaseDB = declarative_base()


class User(BaseDB):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    phone_number = Column(String)
    email = Column(String)
    social_media = Column(String)
    status = Column(String)
    activity = Column(String)
    reg_date = Column(DateTime)
    proxies = Column(String)
    amount_of_friends = Column(Integer)
    already_used_keywords = Column(JSON)
    country = Column(String)
    groups_used = Column(JSON)
    user_link = Column(String)
    gologin_id = Column(String)


class Keyword(BaseDB):
    __tablename__ = 'keywords'
    keyword_id = Column(Integer, primary_key=True)
    keyword = Column(String)
    social_media = Column(String)
    user_id = Column(String)


class Schedule(BaseDB):
    __tablename__ = 'schedule'
    schedule_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String)
    day = Column(Integer)
    time_range = Column(Integer)
    exact_time = Column(String)


class FacebookProfile(BaseDB):
    __tablename__ = 'facebook_profile'
    user_id = Column(Integer, primary_key=True)
    current_location = Column(String)
    native_location = Column(String)
    company = Column(String)
    position = Column(String)
    city = Column(String)
    description = Column(String)
    bio = Column(String)
    avatar = Column(String)


class TwitterProfile(BaseDB):
    __tablename__ = 'twitter_profile'
    user_id = Column(Integer, primary_key=True)
    avatar = Column(String)
    cover = Column(String)
    name = Column(String)
    about_myself = Column(String)
    location = Column(String)


class InstagramProfile(BaseDB):
    __tablename__ = 'instagram_profile'
    user_id = Column(Integer, primary_key=True)


class Feed(BaseDB):
    __tablename__ = 'feed'
    post_id = Column(Integer, primary_key=True)
    user_id = Column(String)
    social_media = Column(String)
    author_name = Column(String)
    text = Column(String)
    image_path = Column(String)
    posts_link = Column(String)
    status = Column(String)
    date = Column(DateTime)
    likes_amount = Column(Integer)
    likes_accounts = Column(JSON)
    comments_amount = Column(Integer)
    comments_accounts = Column(JSON)
    retweets_amount = Column(String)
    text_names = Column(String)
    noun_keywords = Column(String)
    label = Column(String)
    sent_rate = Column(String)
    language = Column(String)


class SelfPosts(BaseDB):
    __tablename__ = 'self_posts'
    post_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    social_media = Column(String)
    text = Column(String)
    filename = Column(String)
    status = Column(String)
    date = Column(String)


class ConversationsPostgres(BaseDB):
    __tablename__ = 'conversations'

    conversation_id = Column(Integer, primary_key=True)
    conversation_name = Column(String)
    post_links = Column(JSON)
    master_accounts = Column(JSON)
    meek_accounts = Column(JSON)
    start_datetime = Column(FLOAT)
    thread = Column(JSON)
    reactions = Column(JSON)
    tmp_data = Column(JSON)


if __name__ == "__main__":
    pass
