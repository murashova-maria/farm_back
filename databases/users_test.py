from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, TIMESTAMP, FLOAT

engine = create_engine('sqlite:///test.db')
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

    # def __init__(self, **kwargs):
    #     super().__init__()
    #     for key, value in kwargs.items():
    #         setattr(self, key, value)

    @classmethod
    def create_user(cls, session, username, password, phone_number=None, social_media=None,
                    status=None, activity=None, reg_date=None, proxies=None,
                    amount_of_friends=0, already_used_keywords: list = None, country=None, groups_used=None,
                    user_link: str = None, gologin_id=None):
        if already_used_keywords is None:
            already_used_keywords = []
        if groups_used is None:
            groups_used = []
        user_node = cls(username=username, password=password, phone_number=phone_number, social_media=social_media,
                        status=status, activity=activity, reg_date=reg_date, proxies=proxies,
                        amount_of_friends=amount_of_friends, already_used_keywords=already_used_keywords,
                        country=country, groups_used=groups_used, user_link=user_link, gologin_id=gologin_id)
        session.add(user_node)
        session.commit()
        return user_node

    @classmethod
    def update_user(cls, session, user_id, **kwargs):
        user_node = session.query(cls).filter_by(user_id=user_id).first()
        if user_node:
            for key, value in kwargs.items():
                setattr(user_node, key, value)
            session.commit()
            return user_node
        else:
            return None

    @classmethod
    def filter_users(cls, session, **kwargs):
        print(cls)
        query = session.query(cls)
        for key, value in kwargs.items():
            query = query.filter(getattr(cls, key) == value)
        return query.all()

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()


if __name__ == '__main__':
    BaseDB.metadata.create_all(engine)
    user_session = sessionmaker(bind=engine)
    user_session = user_session()
    udb = User()
    udb.create_user(user_session, 'NewUser', 'mns90099', '+380973195276')
    for usr in udb.filter_users(user_session, username='penguin_nube'):
        print(usr.username)
