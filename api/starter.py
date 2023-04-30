# LOCAL
from loader import *
from farm.social_media.twitter import *
from farm.social_media.facebook import *
from farm.social_media.instagram import *

try:
    from utils import ready_to_post
except ImportError:
    from .utils import ready_to_post


class Starter:
    def __init__(self, username, password, phone_number, network, proxy=None, country='None'):
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.network = network
        self.pure_proxy = proxy
        if proxy is not None and proxy != 'None':
            proxy = proxy.split(':')
            proxy = {'ip': proxy[0], 'port': proxy[1], 'username': proxy[2], 'password': proxy[3]}
        self.proxy = proxy
        self.country = country

    def _add_user(self, status: str = 'Success'):
        usr = UserDB.filter_users(username=self.username, password=self.password,
                                  phone_number=self.phone_number, network=self.network)
        if usr:
            st = QueuedTask(UserDB, 'update_user', {'user_id': usr['user_id'], 'status': status, 'activity': 'wait',
                                                    'proxy': self.pure_proxy,
                                                    'reg_date': datetime.datetime.now()})
            main_queue.put(st)
            return
        st = QueuedTask(UserDB, 'create_user', [self.username, self.password, self.phone_number,
                                                self.network, status, 'wait', datetime.datetime.now(), self.pure_proxy])
        main_queue.put(st)

    def start_instagram(self):
        inst = Instagram(self.username, self.password, self.phone_number, proxy=self.proxy)
        login_status = inst.login()
        sleep(2)
        if not login_status:
            self._add_user('Banned')
            inst.driver.close()
            return
        self._add_user('Active')
        while True:
            sleep(1)
            try:
                # Get user's DB object.
                user_info = UserDB.filter_users(username=self.username, password=self.password,
                                                phone_number=self.phone_number, social_media='instagram')
                user_info = user_info[0]
                inst.usr_id = user_info['user_id']
                if user_info['activity'] == 'fill_profile':
                    profile = InstagramProfileDB.filter_profiles(user_id=user_info['user_id'])[0]
                    avatar = profile['avatar']
                    name = profile['name']
                    about_myself = profile['about_myself']
                    gender = profile['gender']
                    inst.fill_profile(name, None, about_myself, gender, avatar)
                    task = QueuedTask(UserDB, 'update_user', {'activity': 'wait', 'status': 'done',
                                                              'user_id': inst.usr_id})
                    main_queue.put(task)
                elif user_info['activity'] == 'check_feed':
                    for search_tag in KeywordDB.get_keywords_by_user_id(user_id=user_info['user_id'], only_kw=False):
                        if search_tag['status'] != 'wait':
                            continue
                        inst.handle_posts(search_tag['keyword'], search_tag['amount'])
                        main_queue.put(QueuedTask(KeywordDB, 'update_keyword', {'keyword_id': search_tag['keyword_id'],
                                                                                'status': 'done'}))
                    main_queue.put(QueuedTask(UserDB, 'update_user', {
                        'user_id': inst.usr_id,
                        'status': 'active',
                        'activity': 'wait'
                    }))
                    sleep(5)
                elif user_info['activity'] == 'make_post':
                    posts = SelfPostsDB.filter_posts(user_id=user_info['user_id'], status='do_post')
                    if len(posts) > 0:
                        post = posts[0]
                        inst.make_post(post['text'], post['filename'])
                        main_queue.put(QueuedTask(SelfPostsDB, 'update_post', {'status': 'done',
                                                                               'post_id': post['post_id']}))
                        main_queue.put(QueuedTask(UserDB, 'update_user', {
                            'user_id': inst.usr_id,
                            'status': 'active',
                            'activity': 'wait'
                        }))
                        sleep(3)

            except Exception as ex:
                print(ex)

    def start_facebook(self):
        fb = Facebook(self.username, self.password, self.phone_number, proxy=self.proxy)
        login_status = fb.login()
        sleep(2)
        if not login_status:
            self._add_user('Banned')
            fb.driver.close()
            return
        self._add_user('Active')
        user_info = UserDB.filter_users(username=self.username, password=self.password,
                                        phone_number=self.phone_number, social_media='facebook')[0]
        task = QueuedTask(FacebookProfileDB, 'update_profile', {'name': str(fb.name),
                                                                'user_id': user_info['user_id']})
        main_queue.put(task)
        while True:
            try:
                sleep(2)
                # Get user's DB object.
                user_info = UserDB.filter_users(username=self.username, password=self.password,
                                                phone_number=self.phone_number, social_media='facebook')[0]
                fb.usr_id = user_info['user_id']
                if user_info['activity'] == 'fill_profile':
                    try:
                        profile = FacebookProfileDB.filter_profiles(user_id=user_info['user_id'])
                        if profile:
                            profile = profile[0]
                        else:
                            continue
                        avatar = profile['avatar']
                        current_location = profile['current_location']
                        native_location = profile['native_location']
                        company = profile['company']
                        position = profile['position']
                        city = profile['city']
                        description = profile['description']
                        bio = profile['bio']
                        fb.add_location(current_location, native_location)
                        fb.add_work(company, position, city, description)
                        if avatar != 'None' and avatar:
                            fb.change_pictures(avatar)
                        fb.add_bio(bio)
                    except Exception as ex:
                        print(ex)
                    task = QueuedTask(UserDB, 'update_user', {'activity': 'wait', 'status': 'done',
                                                              'user_id': user_info['user_id']})
                    main_queue.put(task)
                    sleep(3)
                elif user_info['activity'] == 'add_hobbies':
                    profile = FacebookProfileDB.filter_profiles(user_id=user_info['user_id'])[0]
                    hobbies = profile['hobbies']
                    if type(profile['hobbies']) is str:
                        hobbies = profile['hobbies'].split()
                    if hobbies and hobbies != 'None':
                        fb.add_hobbies(hobbies)
                    task = QueuedTask(UserDB, 'update_user', {'activity': 'wait', 'status': 'done',
                                                              'user_id': user_info['user_id']})
                    main_queue.put(task)
                    sleep(3)
                elif user_info['activity'] == 'add_friends':
                    fb.add_friends(max_value=randint(3, 25))
                elif user_info['activity'] == 'search_groups':
                    for search_tag in KeywordDB.get_keywords_by_user_id(user_id=user_info['user_id'], only_kw=False):
                        if search_tag['keyword'] in user_info['groups_used']:
                            continue
                        if search_tag['status'] != 'wait':
                            continue
                        fb.join_groups_by_interests(search_tag['keyword'], search_tag['amount'])
                        if user_info['groups_used'] == 'None':
                            user_info['groups_used'] = []
                        user_info['groups_used'].append(search_tag['keyword'])
                        break
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'user_id': user_info['user_id'], 'status': 'done',
                                                                      'activity': 'wait',
                                                                      'groups_used': user_info['groups_used']}))
                elif user_info['activity'] == 'check_feed':
                    for search_tag in KeywordDB.get_keywords_by_user_id(user_id=user_info['user_id'], only_kw=False):
                        if search_tag['keyword'] in user_info['already_used_keywords']:
                            continue
                        if search_tag['status'] != 'wait':
                            continue
                        fb.collect_posts(search_tag['keyword'], search_tag['amount'])
                        if user_info['already_used_keywords'] == 'None':
                            user_info['already_used_keywords'] = []
                        user_info['already_used_keywords'].append(search_tag['keyword'])
                        break
                    main_queue.put(QueuedTask(UserDB, 'update_user', {
                        'user_id': fb.usr_id,
                        'activity': 'wait',
                        'status': 'active',
                        'already_used_keywords': user_info['already_used_keywords'],
                    }))
                    sleep(5)
                elif user_info['activity'] == 'make_post':
                    main_queue.put(QueuedTask(UserDB, 'update_user', {
                        'user_id': fb.usr_id,
                        'status': 'gardering'
                    }))
                    posts = SelfPostsDB.filter_posts(user_id=user_info['user_id'], status='do_post')
                    if len(posts) > 0:
                        post = posts[0]
                        fb.make_post(post['text'], post['filename'])
                        main_queue.put(QueuedTask(SelfPostsDB, 'update_post', {'status': 'done',
                                                                               'post_id': post['post_id']}))
                        main_queue.put(QueuedTask(UserDB, 'update_user', {
                            'user_id': fb.usr_id,
                            'status': 'active',
                            'activity': 'wait'
                        }))
                elif user_info['activity'] == 'leave_comment':
                    fb.make_comment('https://www.facebook.com/groups/241680586186052/permalink/1898152053872222/',
                                    'Awesome!')
                    main_queue.put(QueuedTask(UserDB, 'update_user', {
                        'user_id': fb.usr_id,
                        'activity': 'wait',
                        'status': 'active',
                    }))
                elif user_info['activity'] == 'scroll_feed':
                    fb.scroll_feed(randint(5, 10))
                for conv_id, conversation in read_json().items():
                    for post_link, values in conversation['tmp_data'].items():
                        index = values['index']
                        next_time_message = values['next_time_message']
                        chain = values['chain']
                        master_accounts = conversation['master_accs']
                        meek_accounts = conversation['meek_accs']
                        thread = conversation['thread']
                        if index >= len(chain):
                            continue
                        if fb.usr_id != chain[index]:
                            continue
                        if next_time_message < datetime.now():
                            continue


            except Exception as ex:
                print('WHILE THREAD: ', ex)

    def start_twitter(self):
        is_country_exist = False
        tw = Twitter(self.username, self.password, self.phone_number, self.proxy, self.country)
        login_status = tw.login()
        sleep(2)
        if not login_status:
            self._add_user('Blocked')
            tw.driver.close()
            return
        self._add_user('Created')
        tw.users_country = self.country
        while True:
            try:
                sleep(1)
                # Get user's DB object.
                user_info = UserDB.filter_users(username=self.username, password=self.password,
                                                phone_number=self.phone_number, social_media='twitter')
                user_info = user_info[0]
                tw.usr_id = user_info['user_id']
                if not is_country_exist:
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'user_id': tw.usr_id, 'country': self.country}))
                    is_country_exist = True
                if user_info['activity'] == 'fill_profile':
                    main_queue.put(QueuedTask(UserDB, 'update_user', {
                        'user_id': tw.usr_id,
                        'status': 'gardering'
                    }))
                    profile = TwitterProfileDB.filter_profiles(user_id=user_info['user_id'])[0]
                    avatar = profile['avatar']
                    cover = profile['cover']
                    name = profile['name']
                    about_myself = profile['about_myself']
                    location = profile['location']
                    tw.fill_profiles_header(avatar, cover,
                                            name, about_myself, location)

                    task = QueuedTask(UserDB, 'update_user', {'activity': 'wait', 'status': 'active',
                                                              'user_id': tw.usr_id})
                    main_queue.put(task)
                elif user_info['activity'] == 'check_feed':
                    main_queue.put(QueuedTask(UserDB, 'update_user', {
                        'user_id': tw.usr_id,
                        'status': 'gardering'
                    }))
                    amount_of_tweets = 0
                    for search_tag in KeywordDB.get_keywords_by_user_id(user_id=user_info['user_id'], only_kw=False):
                        if search_tag['keyword'] in user_info['already_used_keywords']:
                            continue
                        if search_tag['status'] != 'wait':
                            continue
                        for _ in range(search_tag['amount']):
                            amount_of_tweets += tw.collect_posts(search_tag['keyword'])
                            if amount_of_tweets >= search_tag['amount']:
                                break
                        user_info['already_used_keywords'].append(search_tag['keyword'])
                    main_queue.put(QueuedTask(UserDB, 'update_user', {
                        'user_id': tw.usr_id,
                        'activity': 'wait',
                        'status': 'active',
                        'already_used_keywords': user_info['already_used_keywords'],
                    }))
                    sleep(5)
                elif user_info['activity'] == 'make_post':
                    main_queue.put(QueuedTask(UserDB, 'update_user', {
                        'user_id': tw.usr_id,
                        'status': 'gardering'
                    }))
                    posts = SelfPostsDB.filter_posts(user_id=user_info['user_id'], status='do_post')
                    if len(posts) > 0:
                        post = posts[0]
                        tw.make_post(post['text'], post['filename'])
                        main_queue.put(QueuedTask(SelfPostsDB, 'update_post', {'status': 'done',
                                                                               'post_id': post['post_id']}))
                        main_queue.put(QueuedTask(UserDB, 'update_user', {
                            'user_id': tw.usr_id,
                            'status': 'active',
                            'activity': 'wait'
                        }))
                        sleep(2)
            except Exception as ex:
                print(ex)


if __name__ == '__main__':
    pass
