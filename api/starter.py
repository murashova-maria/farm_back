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
    def __init__(self, username, password, phone_number, network, proxy=None):
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.network = network
        if proxy is not None and proxy != 'None':
            proxy = proxy.split(':')
            proxy = {'ip': proxy[0], 'port': proxy[1], 'username': proxy[2], 'password': proxy[3]}
        self.proxy = proxy

    def _add_user(self, status: str = 'Success'):
        usr = UserDB.filter_users(username=self.username, password=self.password,
                                  phone_number=self.phone_number, network=self.network)
        if usr:
            st = QueuedTask(UserDB, 'update_user', {'user_id': usr['user_id'], 'status': status, 'activity': 'wait'})
            main_queue.put(st)
            return
        st = QueuedTask(UserDB, 'create_user', [self.username, self.password, self.phone_number,
                                                self.network, status])
        main_queue.put(st)

    def start_instagram(self):
        inst = Instagram(self.username, self.password, self.phone_number, proxy=self.proxy)
        login_status = inst.login()
        sleep(2)
        if not login_status:
            self._add_user('[ERROR]: Instagram Login is unsuccessful -> Access denied.')
            inst.driver.close()
            return
        self._add_user('[SUCCESS]: Instagram is Logged in')
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
                    inst.fill_profile(IMG_DIR + 'instagram/' + avatar, name, about_myself, gender)
                    task = QueuedTask(UserDB, 'update_user', {'activity': 'wait', 'status': 'done',
                                                              'user_id': inst.usr_id})
                    main_queue.put(task)
                elif user_info['activity'] == 'check_feed':
                    if user_info['search_tag']:
                        inst.collect_posts(user_info['search_tag'])
                    else:
                        inst.collect_posts()
                elif user_info['activity'] == 'make_post':
                    posts = SelfPostsDB.filter_posts(user_id=user_info['user_id'], status='do_post')
                    for post in posts:
                        inst.make_post(post['text'], IMG_DIR + 'instagram/' + post['filename'])
                        main_queue.put(QueuedTask(SelfPostsDB, 'update_post', {'status': 'done',
                                                                               'post_id': post['post_id']}))
                        sleep(3)
            except Exception as ex:
                print(ex)

    def start_facebook(self):
        fb = Facebook(self.username, self.password, self.phone_number, proxy=self.proxy)
        login_status = fb.login()
        sleep(2)
        if not login_status:
            self._add_user('[ERROR]: Twitter Login is unsuccessful -> Access denied.')
            fb.driver.close()
            return
        self._add_user('[SUCCESS]: Twitter is Logged in')
        while True:
            try:
                # Get user's DB object.
                user_info = UserDB.filter_users(username=self.username, password=self.password,
                                                phone_number=self.phone_number, social_media='facebook')[0]
                fb.usr_id = user_info['user_id']
                if user_info['activity'] == 'fill_profile':
                    profile = FacebookProfileDB.filter_profiles(user_id=user_info['user_id'])[0]
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
                        fb.change_pictures(IMG_DIR + 'facebook/' + avatar)
                    fb.add_bio(bio)
                    task = QueuedTask(UserDB, 'update_user', {'activity': 'wait', 'status': 'done',
                                                              'user_id': user_info['user_id']})
                    main_queue.put(task)
                elif user_info['activity'] == 'add_hobbies':
                    profile = FacebookProfileDB.filter_profiles(user_id=user_info['user_id'])[0]
                    hobbies = profile['hobbies'].split()
                    if hobbies and hobbies != 'None':
                        fb.add_hobbies(hobbies)
                    task = QueuedTask(UserDB, 'update_user', {'activity': 'wait', 'status': 'done',
                                                              'user_id': user_info['user_id']})
                    main_queue.put(task)
                elif user_info['activity'] == 'add_friends':
                    fb.add_friends(max_value=100)
                elif user_info['activity'] == 'search_groups':
                    if user_info['search_tag']:
                        fb.join_groups_by_interests(user_info['search_tag'])
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'user_id': user_info['user_id'], 'status': 'done',
                                                                      'activity': 'wait'}))
                elif user_info['activity'] == 'check_feed':
                    if user_info['search_tag']:
                        fb.collect_posts(user_info['search_tag'])
                    else:
                        fb.collect_posts()
            except Exception as ex:
                print(ex)

    def start_twitter(self):
        tw = Twitter(self.username, self.password, self.phone_number, self.proxy)
        login_status = tw.login()
        sleep(2)
        if not login_status:
            self._add_user('[ERROR]: Twitter Login is unsuccessful -> Access denied.')
            tw.driver.close()
            return
        self._add_user('[SUCCESS]: Twitter is Logged in')
        while True:
            sleep(1)
            try:
                # Get user's DB object.
                user_info = UserDB.filter_users(username=self.username, password=self.password,
                                                phone_number=self.phone_number, social_media='twitter')
                user_info = user_info[0]
                tw.usr_id = user_info['user_id']
                if user_info['activity'] == 'fill_profile':
                    profile = TwitterProfileDB.filter_profiles(user_id=user_info['user_id'])[0]
                    avatar = profile['avatar']
                    cover = profile['cover']
                    name = profile['name']
                    about_myself = profile['about_myself']
                    location = profile['location']
                    tw.fill_profiles_header(IMG_DIR + 'twitter/' + avatar, IMG_DIR + 'twitter/' + cover,
                                            name, about_myself, location)

                    task = QueuedTask(UserDB, 'update_user', {'activity': 'wait', 'status': 'done',
                                                              'user_id': tw.usr_id})
                    main_queue.put(task)
                elif user_info['activity'] == 'check_feed':
                    if user_info['search_tag']:
                        tw.collect_posts(user_info['search_tag'])
                    else:
                        tw.collect_posts()
                elif user_info['activity'] == 'make_post':
                    posts = SelfPostsDB.filter_posts(user_id=user_info['user_id'], status='do_post')
                    for post in posts:
                        tw.make_post(post['text'], IMG_DIR + 'twitter/' + post['filename'])
                        main_queue.put(QueuedTask(SelfPostsDB, 'update_post', {'status': 'done',
                                                                               'post_id': post['post_id']}))
                        sleep(3)
            except Exception as ex:
                print(ex)


if __name__ == '__main__':
    pass
