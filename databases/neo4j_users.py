# USER ID
import uuid

# DATABASE
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher

# OTHER
from random import randint
from datetime import datetime


class User:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(self.graph)

    def _attach_profile(self, user_id, network):
        if network == 'twitter':
            tp = TwitterProfile(self.graph)
            tp.create_profile(user_id=user_id)
        elif network == 'facebook':
            fb = FacebookProfile(self.graph)
            fb.create_profile(user_id=user_id)
        else:
            inst = InstagramProfile(self.graph)
            inst.create_profile(user_id)

    def create_user(self, username, password, phone_number='None', social_media='None',
                    status='None', activity='None', reg_date='None', proxies='None', search_tag='None'):
        user_id = str(uuid.uuid4())
        check_usr = self.matcher.match("User", username=username, password=password, phone_number=phone_number,
                                       social_media=social_media).first()
        if check_usr:
            return check_usr
        user_node = Node("User", user_id=user_id, username=username, password=password,
                         phone_number=phone_number, social_media=social_media,
                         status=status, activity=activity, reg_date=reg_date,
                         proxies=proxies, search_tag=search_tag)
        self.graph.create(user_node)
        self._attach_profile(user_id=user_id, network=social_media)
        return user_node

    def add_keyword_to_user(self, user_id, keyword, status='wait'):
        user_node = self.graph.nodes.match('User', id=user_id).first()
        keyword_node = Node('Keyword', id=randint(0, 2147483647), keyword=keyword, status=status)
        rel = Relationship(user_node, 'HAS_KEYWORD', keyword_node)
        self.graph.create(rel)

    def update_user(self, user_id, **kwargs):
        user_node = self.matcher.match("User", user_id=user_id).first()
        if user_node:
            for key, value in kwargs.items():
                user_node[key] = value
            self.graph.push(user_node)
            return user_node
        else:
            return None

    def filter_users(self, **kwargs):
        query = "MATCH (u:User) WHERE "
        params = {"params_" + key: value for key, value in kwargs.items()}
        for key, value in kwargs.items():
            query += f"u.{key} = $params_{key} AND "
        query = query[:-5]
        query += " RETURN u"
        result = self.graph.run(query, **params)
        return [record["u"] for record in result]

    def get_all(self):
        return list(self.matcher.match('User'))


class TwitterProfile:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(self.graph)

    def create_profile(self, user_id, avatar='None', cover='None', name='None',
                       about_myself='None', location='None'):
        profile_node = Node("TwitterProfile", user_id=user_id,
                            avatar=avatar, cover=cover, name=name,
                            about_myself=about_myself, location=location)
        self.graph.create(profile_node)
        return profile_node

    def update_profile(self, **kwargs):
        profile_node = self.matcher.match("TwitterProfile", user_id=kwargs['user_id']).first()
        if profile_node:
            for key, value in kwargs.items():
                profile_node[key] = value
            self.graph.push(profile_node)
            return profile_node
        else:
            return None

    def filter_profiles(self, **kwargs):
        query = "MATCH (p:TwitterProfile) WHERE "
        params = {"params_" + key: value for key, value in kwargs.items()}
        for key, value in kwargs.items():
            query += f"p.{key} = $params_{key} AND "
        query = query[:-5]
        query += " RETURN p"
        result = self.graph.run(query, **params)
        return [record["p"] for record in result]

    def get_all(self):
        return list(self.matcher.match('TwitterProfile'))


class FacebookProfile:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(self.graph)

    def create_profile(self, user_id, current_location='None', native_location='None',
                       company='None', position='None', city='None',
                       description='None', bio='None', avatar='None', hobbies='None'):
        profile_node = Node("FacebookProfile", user_id=user_id,
                            current_location=current_location, native_location=native_location,
                            company=company, position=position, city=city,
                            description=description, bio=bio, avatar=avatar, hobbies=hobbies)
        self.graph.create(profile_node)
        return profile_node

    def update_profile(self, user_id, **kwargs):
        profile_node = self.matcher.match("FacebookProfile", user_id=user_id).first()
        if profile_node:
            for key, value in kwargs.items():
                profile_node[key] = value
            self.graph.push(profile_node)
            return profile_node
        else:
            return None

    def filter_profiles(self, **kwargs):
        query = "MATCH (p:FacebookProfile) WHERE "
        params = {"params_" + key: value for key, value in kwargs.items()}
        for key, value in kwargs.items():
            query += f"p.{key} = $params_{key} AND "
        query = query[:-5]
        query += " RETURN p"
        result = self.graph.run(query, **params)
        return [record["p"] for record in result]

    def get_all(self):
        return list(self.matcher.match('FacebookProfile'))


class InstagramProfile:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(self.graph)

    def create_profile(self, user_id, avatar='None', name='None',
                       about_myself='None', gender='None'):
        profile_node = Node("InstagramProfile", user_id=user_id,
                            avatar=avatar, name=name, about_myself=about_myself,
                            gender=gender)
        self.graph.create(profile_node)
        return profile_node

    def update_profile(self, **kwargs):
        profile_node = self.matcher.match("InstagramProfile", user_id=kwargs['user_id']).first()
        if profile_node:
            for key, value in kwargs.items():
                profile_node[key] = value
            self.graph.push(profile_node)
            return profile_node
        else:
            return None

    def filter_profiles(self, **kwargs):
        query = "MATCH (p:InstagramProfile) WHERE "
        params = {"params_" + key: value for key, value in kwargs.items()}
        for key, value in kwargs.items():
            query += f"p.{key} = $params_{key} AND "
        query = query[:-5]
        query += " RETURN p"
        result = self.graph.run(query, **params)
        return [record["p"] for record in result]

    def get_all(self):
        return list(self.matcher.match('InstagramProfile'))


class Feed:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(self.graph)

    def create_post(self, user_id, social_media, author_name='None', text='None', image_path='None',
                    posts_link='None', status='None', date='None', likes_amount='None', likes_accounts='None',
                    comments_amount='None', comments_accounts='None', retweets_amount='None', text_names='None',
                    noun_keywords='None', label='None', sent_rate='None', language='None'):
        post_id = str(uuid.uuid4())
        post_node = Node("Post", post_id=post_id, user_id=user_id, social_media=social_media,
                         author_name=author_name, text=text, image_path=image_path,
                         posts_link=posts_link, status=status, date=date, likes_amount=likes_amount,
                         likes_accounts=likes_accounts, comments_amount=comments_amount,
                         comments_accounts=comments_accounts, retweets_amount=retweets_amount,
                         text_names=text_names, noun_keywords=noun_keywords, label=label,
                         sent_rate=sent_rate, language=language)
        self.graph.create(post_node)
        return post_node

    def update_post(self, post_id, **kwargs):
        post_node = self.matcher.match("Post", post_id=post_id).first()
        if post_node:
            for key, value in kwargs.items():
                post_node[key] = value
            self.graph.push(post_node)
            return post_node
        else:
            return None

    def filter_posts(self, **kwargs):
        query = "MATCH (p:Post) WHERE "
        params = {"params_" + key: value for key, value in kwargs.items()}
        for key, value in kwargs.items():
            query += f"p.{key} = $params_{key} AND "
        query = query[:-5]
        query += " RETURN p"
        result = self.graph.run(query, **params)
        return [record["p"] for record in result]

    def get_all(self):
        return list(self.matcher.match('Post'))


class SelfPosts:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(self.graph)

    def create_post(self, user_id, social_media, text='None', filename='None',
                    status='None', date='None'):
        post_id = str(uuid.uuid4())
        post_node = Node("SelfPost", post_id=post_id, user_id=user_id, social_media=social_media,
                         text=text, filename=filename, status=status, date=date)
        self.graph.create(post_node)
        return post_node

    def update_post(self, post_id, **kwargs):
        post_node = self.matcher.match("SelfPost", post_id=post_id).first()
        if post_node:
            for key, value in kwargs.items():
                post_node[key] = value
            self.graph.push(post_node)
            return post_node
        else:
            return None

    def filter_posts(self, **kwargs):
        query = "MATCH (p:SelfPost) WHERE "
        params = {"params_" + key: value for key, value in kwargs.items()}
        for key, value in kwargs.items():
            query += f"p.{key} = $params_{key} AND "
        query = query[:-5]
        query += " RETURN p"
        result = self.graph.run(query, **params)
        return [record["p"] for record in result]

    def get_all(self):
        return list(self.matcher.match('SelfPost'))


class Conversation:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)

    def create_chat(self, chat_id):
        chat_node = Node('Chat', id=chat_id)
        self.graph.create(chat_node)

    def add_user_to_chat(self, chat_id, user_id, message_text=None, delay=None):
        chat_node = self.graph.nodes.match('Chat', id=chat_id).first()
        user_node = Node('User', id=user_id)
        rel = Relationship(chat_node, 'HAS_USER', user_node)
        self.graph.create(rel)

    def add_message_to_user(self, chat_id, user_id, message_text, delay):
        user_node = self.graph.nodes.match('User', id=user_id).first()
        message_node = Node('Message', message_id=randint(0, 2147483647), message_text=message_text, delay=delay,
                            status='wait')
        rel = Relationship(user_node, 'HAS_MESSAGE', message_node)
        chat_node = self.graph.nodes.match('Chat', id=chat_id).first()
        self.graph.create(rel)
        self.graph.create(Relationship(chat_node, 'HAS_MESSAGE', message_node))

    def find_chats(self, **kwargs):
        query = "MATCH (c:Chat)"
        params = {}
        for k, v in kwargs.items():
            query += f" WHERE c.{k} = ${k}"
            params[k] = v
        query += " RETURN c"
        result = self.graph.run(query, params)
        return [r[0] for r in result]

    def get_all_chats(self):
        query = "MATCH (c:Chat) RETURN c"
        result = self.graph.run(query)
        return [r[0] for r in result]

    def get_chat_info(self, chat_id, delay_limit=None):
        # find chat node
        chat_node = self.graph.nodes.match('Chat', id=chat_id).first()
        if not chat_node:
            return None

        # find users and their messages in the chat
        results = self.rel_matcher.match((chat_node, ), 'HAS_USER')
        users = []
        for rel in results:
            user_node = rel.end_node
            messages = []
            if delay_limit is not None:
                message_results = self.rel_matcher.match((user_node, ), 'HAS_MESSAGE')
            else:
                message_results = self.rel_matcher.match((user_node, ), 'HAS_MESSAGE')
            for message_rel in message_results:
                message_node = message_rel.end_node
                messages.append({
                    'message_id': message_node.get('message_id'),
                    'message_text': message_node.get('message_text'),
                    'delay': message_node.get('delay')
                })
            users.append({
                'id': user_node.get('id'),
                'messages': messages
            })

        # build chat info dictionary
        chat_info = {
            'id': chat_node.get('id'),
            'users': users
        }
        return chat_info


if __name__ == '__main__':
    pass
