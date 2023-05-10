# SYSTEM
import os
import traceback
import uuid

# DATABASE
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, JSON, FLOAT, MetaData

# engine = create_engine('sqlite:///bots_farm.db', connect_args={'check_same_thread': False})
engine = create_engine('postgresql://postgres:6nvj8nMm@65.109.34.120:5432', poolclass=QueuePool)
BaseDB = declarative_base()


class UserBase(BaseDB):
    __tablename__ = 'users'
    user_id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    username = Column(String)
    password = Column(String)
    phone_number = Column(String)
    email = Column(String, default=None)
    social_media = Column(String)
    status = Column(String, default='active')
    activity = Column(String, default='wait')
    reg_date = Column(FLOAT)
    proxies = Column(String, default=None)
    amount_of_friends = Column(String, default='0')
    already_used_keywords = Column(JSON, default=[])
    country = Column(String)
    groups_used = Column(JSON, default=[])
    user_link = Column(String)
    gologin_id = Column(String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _attach_profile(user_id, network):
        if network == 'twitter':
            tp = TwitterProfileBase()
            tp.create_profile(user_id=user_id)
        elif network == 'facebook':
            fb = FacebookProfileBase()
            fb.create_profile(user_id=user_id)
        else:
            inst = InstagramProfileBase()
            inst.create_profile(user_id=user_id)

    @classmethod
    def create_user(cls, **kwargs):
        is_user_exist = session.query(cls).filter_by(username=kwargs['username'], password=kwargs['password'],
                                                     social_media=kwargs['social_media']).first()
        if is_user_exist:
            return cls.update_user(is_user_exist.user_id)
        user_node = cls(**kwargs)
        session.add(user_node)
        session.commit()
        cls._attach_profile(user_node.user_id, user_node.social_media)
        return user_node

    @classmethod
    def update_user(cls, user_id, **kwargs):
        user_node = session.query(cls).get(user_id)
        if user_node:
            for key, value in kwargs.items():
                if key == 'user_id':
                    continue
                setattr(user_node, key, value)
            session.commit()
        return user_node

    @classmethod
    def filter_users(cls, **kwargs):
        try:
            return [{key: value for key, value in usr.__dict__.items() if '_sa_instance_state' not in key}
                    for usr in session.query(cls).filter_by(**kwargs)]
        except Exception as ex:
            traceback.print_exc()
            return []

    @classmethod
    def get_all(cls):
        return [{key: value for key, value in elem.__dict__.items() if '_sa_instance_state' not in key}
                for elem in session.query(cls).all()]


class FacebookProfileBase(BaseDB):
    __tablename__ = 'facebook_profile'
    user_id = Column(String(32), primary_key=True)
    name = Column(String)
    current_location = Column(String)
    native_location = Column(String)
    company = Column(String)
    position = Column(String)
    city = Column(String)
    description = Column(String)
    bio = Column(String)
    avatar = Column(String)
    hobbies = Column(JSON)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create_profile(cls, **kwargs):
        is_profile_exist = session.query(cls).filter_by(user_id=kwargs['user_id']).first()
        if is_profile_exist:
            return cls.update_profile(is_profile_exist.user_id)
        user_node = cls(**kwargs)
        session.add(user_node)
        session.commit()
        return user_node

    @classmethod
    def update_profile(cls, user_id, **kwargs):
        user_node = session.query(cls).get(user_id)
        if user_node:
            for key, value in kwargs.items():
                if key == 'user_id':
                    continue
                setattr(user_node, key, value)
            session.commit()
        return user_node

    @classmethod
    def filter_profiles(cls, **kwargs):
        try:
            return [{key: value for key, value in usr.__dict__.items() if '_sa_instance_state' not in key}
                    for usr in session.query(cls).filter_by(**kwargs)]
        except Exception as ex:
            traceback.print_exc()
            return []

    @classmethod
    def get_all(cls):
        return [{key: value for key, value in elem.__dict__.items() if '_sa_instance_state' not in key}
                for elem in session.query(cls).all()]


class TwitterProfileBase(BaseDB):
    __tablename__ = 'twitter_profile'
    user_id = Column(String(32), primary_key=True)
    avatar = Column(String)
    cover = Column(String)
    name = Column(String)
    about_myself = Column(String)
    location = Column(String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create_profile(cls, **kwargs):
        is_profile_exist = session.query(cls).filter_by(user_id=kwargs['user_id']).first()
        if is_profile_exist:
            return cls.update_profile(is_profile_exist.user_id)
        user_node = cls(**kwargs)
        session.add(user_node)
        session.commit()
        return user_node

    @classmethod
    def update_profile(cls, user_id, **kwargs):
        user_node = session.query(cls).get(user_id)
        if user_node:
            for key, value in kwargs.items():
                if key == 'user_id':
                    continue
                setattr(user_node, key, value)
            session.commit()
        return user_node

    @classmethod
    def filter_profiles(cls, **kwargs):
        try:
            return [{key: value for key, value in usr.__dict__.items() if '_sa_instance_state' not in key}
                    for usr in session.query(cls).filter_by(**kwargs)]
        except Exception as ex:
            traceback.print_exc()
            return []

    @classmethod
    def get_all(cls):
        return [{key: value for key, value in elem.__dict__.items() if '_sa_instance_state' not in key}
                for elem in session.query(cls).all()]


class InstagramProfileBase(BaseDB):
    __tablename__ = 'instagram_profile'
    user_id = Column(String(32), primary_key=True)
    avatar = Column(String)
    name = Column(String)
    about_myself = Column(String)
    gender = Column(String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create_profile(cls, **kwargs):
        is_profile_exist = session.query(cls).filter_by(user_id=kwargs['user_id']).first()
        if is_profile_exist:
            return cls.update_profile(is_profile_exist.user_id)
        user_node = cls(**kwargs)
        session.add(user_node)
        session.commit()
        return user_node

    @classmethod
    def update_profile(cls, user_id, **kwargs):
        user_node = session.query(cls).get(user_id)
        if user_node:
            for key, value in kwargs.items():
                if key == 'user_id':
                    continue
                setattr(user_node, key, value)
            session.commit()
        return user_node

    @classmethod
    def filter_profiles(cls, **kwargs):
        try:
            return [{key: value for key, value in usr.__dict__.items() if '_sa_instance_state' not in key}
                    for usr in session.query(cls).filter_by(**kwargs)]
        except Exception as ex:
            traceback.print_exc()
            return []

    @classmethod
    def get_all(cls):
        return [{key: value for key, value in elem.__dict__.items() if '_sa_instance_state' not in key}
                for elem in session.query(cls).all()]


class SelfPostsBase(BaseDB):
    __tablename__ = 'self_posts'
    post_id = Column(String(32), default=lambda: uuid.uuid4().hex, primary_key=True)
    user_id = Column(String(32))
    text = Column(String)
    filename = Column(String)
    status = Column(String, default=None)
    day = Column(Integer, default=None)
    time_range = Column(Integer, default=None)
    exact_time = Column(String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create_post(cls, **kwargs):
        day = kwargs.get('day')
        time_range = kwargs.get('time_range')
        get_post = cls.filter_posts(day=day, time_range=time_range)
        if get_post:
            cls.delete_post(get_post[0]['post_id'])
        post_node = cls(**kwargs)
        session.add(post_node)
        session.commit()
        return post_node

    @classmethod
    def update_post(cls, post_id, **kwargs):
        post_node = session.query(cls).get(post_id)
        if post_node:
            for key, value in kwargs.items():
                if key == 'post_id':
                    continue
                setattr(post_node, key, value)
            session.commit()
        return post_node

    @classmethod
    def filter_posts(cls, **kwargs):
        try:
            return [{key: value for key, value in usr.__dict__.items() if '_sa_instance_state' not in key}
                    for usr in session.query(cls).filter_by(**kwargs)]
        except Exception as ex:
            traceback.print_exc()
            return []

    @classmethod
    def get_all(cls):
        return [{key: value for key, value in elem.__dict__.items() if '_sa_instance_state' not in key}
                for elem in session.query(cls).all()]

    @classmethod
    def delete_post(cls, post_id):
        try:
            post = session.query(cls).get(post_id)
            session.delete(post)
        except Exception as ex:
            pass


class KeywordBase(BaseDB):
    __tablename__ = 'keyword'
    keyword_id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String)
    amount = Column(Integer, default=20)
    status = Column(String, default='wait')
    twitter_user = Column(String, default=None)
    facebook_user = Column(String, default=None)
    instagram_user = Column(String, default=None)

    @classmethod
    def filter_keywords(cls, **kwargs):
        try:
            return [{key: value for key, value in usr.__dict__.items() if '_sa_instance_state' not in key}
                    for usr in session.query(cls).filter_by(**kwargs)]
        except Exception as ex:
            traceback.print_exc()
            return []

    @classmethod
    def create_keyword(cls, **kwargs):
        keyword_exist = session.query(cls).filter_by(keyword=kwargs.get('keyword')).first()
        if keyword_exist:
            return cls.update_keyword(keyword_id=keyword_exist.keyword_id, **kwargs)
        keyword_node = cls(**kwargs)
        session.add(keyword_node)
        session.commit()
        return keyword_node

    @classmethod
    def add_keyword_to_user(cls, keyword_id, user_id, network):
        get_keyword = session.query(cls).filter_by(keyword_id=keyword_id).first()
        if network == 'twitter':
            get_keyword.twitter_user = user_id
        elif network == 'facebook':
            get_keyword.facebook_user = user_id
        elif network == 'instagram':
            get_keyword.instagram_user = user_id
        else:
            return None
        session.commit()

    @classmethod
    def update_keyword(cls, keyword_id, **kwargs):
        user_node = session.query(cls).get(keyword_id)
        if user_node:
            for key, value in kwargs.items():
                if key == 'keyword_id':
                    continue
                setattr(user_node, key, value)
            session.commit()
        return user_node

    @classmethod
    def get_keywords_by_user_id(cls, user_id, only_kw=False):
        return [keyword for keyword in cls.get_all_keywords() if keyword['twitter_user'] == user_id or
                keyword['facebook_user'] == user_id or keyword['instagram_user'] == user_id]

    @classmethod
    def get_all_keywords(cls):
        return [{key: value for key, value in elem.__dict__.items() if '_sa_instance_state' not in key}
                for elem in session.query(cls).all()]

    @classmethod
    def unpin_keyword_from_user(cls, keyword_id, user_id):
        get_keyword = session.query(cls).filter_by(keyword_id=keyword_id).first()
        if get_keyword:
            if get_keyword.instagram_user == user_id:
                get_keyword.instagram_user = None
            elif get_keyword.twitter_user == user_id:
                get_keyword.twitter_user = None
            elif get_keyword.facebook_user == user_id:
                get_keyword.facebook_user = None
            session.commit()

    @classmethod
    def delete_keyword(cls, keyword_id):
        get_keyword = session.query(cls).get(keyword_id)
        if get_keyword:
            session.delete(get_keyword)
            session.commit()


class ScheduleBase(BaseDB):
    __tablename__ = 'schedules'
    schedule_id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String)
    action = Column(String)
    day = Column(Integer)
    time_range = Column(Integer)
    exact_time = Column(String)
    status = Column(String, default=None)
    scroll_minutes = Column(String, default='0')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create_schedule(cls, user_id, **kwargs):
        kwargs.update({'user_id': user_id})
        day = int(kwargs.get('day'))
        time_range = int(kwargs.get('time_range'))
        test_node = session.query(cls).filter_by(day=day, time_range=time_range, user_id=user_id).first()
        if test_node:
            return cls.update_schedule(test_node.schedule_id, **kwargs)
        node = cls(**kwargs)
        session.add(node)
        session.commit()
        return node

    @classmethod
    def update_schedule(cls, schedule_id, **kwargs):
        schedule_node = session.query(cls).get(schedule_id)
        if schedule_node:
            for key, value in kwargs.items():
                if key == 'schedule_id':
                    continue
                setattr(schedule_node, key, value)
            session.commit()
        return schedule_node

    @classmethod
    def filter_schedules(cls, **kwargs):
        try:
            return [{key: value for key, value in usr.__dict__.items() if '_sa_instance_state' not in key}
                    for usr in session.query(cls).filter_by(**kwargs) if usr]
        except Exception as ex:
            print("HERE IT IS USERS_TEST.PY TRACEBACK: ")
            traceback.print_exc()
            return []

    @classmethod
    def get_all_schedules(cls):
        return [{key: value for key, value in elem.__dict__.items() if '_sa_instance_state' not in key}
                for elem in session.query(cls).all()]

    @classmethod
    def delete_schedule(cls, schedule_id):
        get_keyword = session.query(cls).get(schedule_id)
        if get_keyword:
            session.delete(get_keyword)
            session.commit()


# if 'bots_farm.db' not in os.listdir():
#     BaseDB.metadata.create_all(engine)
# UserBase.__table__.drop(engine)
# FacebookProfileBase.__table__.drop(engine)
# TwitterProfileBase.__table__.drop(engine)
# InstagramProfileBase.__table__.drop(engine)
# SelfPostsBase.__table__.drop(engine)
# KeywordBase.__table__.drop(engine)
# ScheduleBase.__table__.drop(engine)
BaseDB.metadata.create_all(engine)
user_session = sessionmaker(bind=engine)
session = user_session()


if __name__ == '__main__':
    print(ScheduleBase().filter_schedules(status='None'))
