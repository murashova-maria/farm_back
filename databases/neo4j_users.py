# USER ID
import uuid

# DATABASE
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher

# OTHER
from random import randint


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
                    status='None', activity='None', reg_date='None', proxies='None', search_tag='None',
                    amount_of_friends=0, already_used_keywords: list = None):
        if already_used_keywords is None:
            already_used_keywords = []
        user_id = str(uuid.uuid4())
        check_usr = self.matcher.match("User", username=username, password=password, phone_number=phone_number,
                                       social_media=social_media).first()
        if check_usr:
            return check_usr
        user_node = Node("User", user_id=user_id, username=username, password=password,
                         phone_number=phone_number, social_media=social_media,
                         status=status, activity=activity, reg_date=reg_date,
                         proxies=proxies, search_tag=search_tag, amount_of_friends=amount_of_friends,
                         already_used_keywords=already_used_keywords)
        self.graph.create(user_node)
        self._attach_profile(user_id=user_id, network=social_media)
        return user_node

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


class Keyword:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(self.graph)

    def add_keyword_to_user(self, keyword, user_id=None, amount=15, status='wait'):
        if user_id:
            user_node = self.graph.nodes.match('User', user_id=user_id).first()
            keyword_node = self.matcher.match('Keyword', keyword=keyword).first()
            if keyword_node is None:
                keyword_node = Node('Keyword', keyword_id=randint(0, 2147483647), keyword=keyword, status=status,
                                    amount=amount)
                self.graph.create(keyword_node)
            rel = Relationship(user_node, 'HAS_KEYWORD', keyword_node)
            self.graph.create(rel)
        else:
            keyword_node = self.matcher.match('Keyword', keyword=keyword).first()
            if keyword_node is None:
                keyword_node = Node('Keyword', keyword_id=randint(0, 2147483647), keyword=keyword,
                                    status=status, amount=amount)
                self.graph.create(keyword_node)

    def filter_keywords(self, **kwargs):
        query = "MATCH (u:Keyword) WHERE "
        params = {"params_" + key: value for key, value in kwargs.items()}
        for key, value in kwargs.items():
            query += f"u.{key} = $params_{key} AND "
        query = query[:-5]
        query += " RETURN u"
        result = self.graph.run(query, **params)
        return [record["u"] for record in result]

    def get_users_by_keyword(self, keyword):
        query = """
                MATCH (u:User)-[:HAS_KEYWORD]->(k:Keyword)
                WHERE k.keyword = $keyword
                RETURN u
                """
        result = self.graph.run(query, keyword=keyword)
        return [record["u"] for record in result]

    def get_all_keywords(self):
        return list(self.matcher.match('Keyword'))

    def get_all_keywords_with_users(self):
        query = """
                MATCH (u:User)-[:HAS_KEYWORD]->(k:Keyword)
                OPTIONAL MATCH (u)-[:HAS_PROFILE]->(p)
                RETURN k.keyword_id as keyword_id, k.keyword as keyword,
                       k.amount as amount, k.status as status,
                       u.user_id as user_id, u.username as username, 
                       u.phone_number as phone_number, u.social_media as social_media,
                       u.status as user_status, u.activity as user_activity,
                       u.reg_date as reg_date, u.proxies as proxies, u.search_tag as search_tag,
                       p.avatar as avatar
                """
        result = self.graph.run(query)

        keywords_dict = {}
        for record in result:
            keyword_id = record["keyword_id"]
            keyword = record["keyword"]
            amount = record["amount"]
            status = record["status"]

            if keyword not in keywords_dict:
                keywords_dict[keyword] = {"keyword_id": keyword_id, "keyword_value": keyword,
                                          "amount": amount, "status": status, "users": []}

            user_id = record["user_id"]
            username = record["username"]
            phone_number = record["phone_number"]
            social_media = record["social_media"]
            user_status = record["user_status"]
            user_activity = record["user_activity"]
            reg_date = record["reg_date"]
            proxies = record["proxies"]
            search_tag = record["search_tag"]
            avatar = record["avatar"]

            user_dict = {"user_id": user_id, "username": username, "phone_number": phone_number,
                         "social_media": social_media, "status": user_status, "activity": user_activity,
                         "reg_date": reg_date, "proxies": proxies, "search_tag": search_tag}

            if avatar is not None:
                user_dict["avatar"] = avatar

            keywords_dict[keyword]["users"].append(user_dict)

        result_list = []
        for keyword, data in keywords_dict.items():
            result_list.append(data)
        return result_list

    def get_keywords_by_user_id(self, user_id, only_kw=True):
        query = """
                MATCH (b:User)-[:HAS_KEYWORD]->(k:Keyword)
                WHERE b.user_id = $user_id
                RETURN k.keyword as keyword
                """
        if not only_kw:
            query = query.replace('k.keyword as keyword', 'k as keyword')
        result = self.graph.run(query, user_id=user_id)
        return [record["keyword"] for record in result]

    def _get_profile_by_user_id(self, user_id, media):
        if media == "twitter":
            profile_node = self.matcher.match("TwitterProfile", user_id=user_id).first()
        elif media == "facebook":
            profile_node = self.matcher.match("FacebookProfile", user_id=user_id).first()
        else:
            profile_node = self.matcher.match("InstagramProfile", user_id=user_id).first()
        return profile_node

    def delete_keywords(self, keyword_id):
        keyword_node = self.matcher.match('Keyword', keyword_id=keyword_id).first()
        if keyword_node:
            self.graph.delete(keyword_node)
            return True
        return False

    def unpin_word_from_user(self, user_id, keyword_id):
        query = """
                MATCH (u:User)-[r:HAS_KEYWORD]->(k:Keyword)
                WHERE u.user_id = $user_id AND k.keyword_id = $keyword_id
                DELETE r
                """
        self.graph.run(query, user_id=user_id, keyword_id=keyword_id)

    def update_keyword(self, keyword_id, **kwargs):
        keyword_node = self.matcher.match('Keyword', keyword_id=keyword_id).first()
        if keyword_node:
            for key, value in kwargs.items():
                keyword_node[key] = value
            self.graph.push(keyword_node)
            return keyword_node
        else:
            return None


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
                    noun_keywords='None', label='None', sent_rate='None', language='None', tag='None'):
        post_id = str(uuid.uuid4())
        post_node = Node("Post", post_id=post_id, user_id=user_id, social_media=social_media,
                         author_name=author_name, text=text, image_path=image_path,
                         posts_link=posts_link, status=status, date=date, likes_amount=likes_amount,
                         likes_accounts=likes_accounts, comments_amount=comments_amount,
                         comments_accounts=comments_accounts, retweets_amount=retweets_amount,
                         text_names=text_names, noun_keywords=noun_keywords, label=label,
                         sent_rate=sent_rate, language=language, tag=tag)
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

    def create_post(self, user_id, text='None', filename='None',
                    status='None', day='None', time_range='None', exact_time='None'):
        post_id = str(uuid.uuid4())
        post_node = Node("SelfPost", post_id=post_id, user_id=user_id, text=text, filename=filename, status=status, day=day, time_range=time_range,
                         exact_time=exact_time)
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

    def create_chat(self):
        chat_id = randint(0, 2147483647)
        chat_node = Node('Chat', chat_id=chat_id)
        self.graph.create(chat_node)

    def add_user_to_chat(self, chat_id, user_id):
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


class Schedule:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(self.graph)

    def update_schedule(self, schedule_id, **kwargs):
        existing_schedule = self.graph.nodes.match("Schedule", schedule_id=schedule_id).first()
        if existing_schedule is None:
            return None

        for key, value in kwargs.items():
            existing_schedule[key] = value
        self.graph.push(existing_schedule)
        return existing_schedule

    def create_schedule(self, user_id, action, day, time_range, exact_time, status='None'):
        test_node = self.filter_schedules(user_id=user_id, day=day, time_range=time_range)
        if len(test_node) > 0:
            params = {}
            if action != 'None':
                params.update({'action': action})
            if exact_time != 'None':
                params.update({'exact_time': exact_time})
            params.update({'status': status})
            schedule_id = test_node[0]['schedule_id']
            return self.update_schedule(schedule_id, **params)
        schedule_id = randint(0, 2147483647)
        post_node = Node("Schedule", schedule_id=schedule_id, user_id=user_id, action=action,
                         day=day, time_range=time_range, exact_time=exact_time, status=status)
        self.graph.create(post_node)
        return post_node

    def filter_schedules(self, **kwargs):
        query = "MATCH (p:Schedule) WHERE "
        params = {"params_" + key: value for key, value in kwargs.items()}
        for key, value in kwargs.items():
            query += f"p.{key} = $params_{key} AND "
        query = query[:-5]
        query += " RETURN p"
        result = self.graph.run(query, **params)
        return [record["p"] for record in result]

    def get_all_schedules(self):
        query = "MATCH (p:Schedule) RETURN p"
        result = self.graph.run(query)
        return [record["p"] for record in result]


if __name__ == '__main__':
    pass
