# OTHER
import datetime
import traceback
from pprint import pprint

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
    def __init__(self, username, password, phone_number, network, proxy=None, country='None', gologin_profile_id=None):
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
        self.gologin_profile_id = gologin_profile_id

    def _add_user(self, status: str = 'Success'):
        usr = UserDB.filter_users(username=self.username, password=self.password,
                                  phone_number=self.phone_number, social_media=self.network)
        if usr:
            st = QueuedTask(UserDB, 'update_user', {'user_id': usr[0]['user_id'], 'status': status, 'activity': 'wait',
                                                    'proxy': self.pure_proxy,
                                                    'reg_date': datetime.datetime.now().timestamp()})
            main_queue.put(st)
            return
        st = QueuedTask(UserDB, 'create_user', {
            'username': self.username,
            'password': self.password,
            'phone_number': self.phone_number,
            'social_media': self.network,
            'status': status,
            'reg_date': datetime.datetime.now().timestamp(),
            'gologin_id': self.gologin_profile_id,
            'country': self.country
        })
        main_queue.put(st)

    def start_instagram(self):
        inst = Instagram(self.username, self.password, self.phone_number, proxy=self.proxy,
                         gologin_id=self.gologin_profile_id)
        login_status = inst.login()
        sleep(2)
        if not login_status:
            self._add_user('Banned')
            try:
                inst.driver.quit()
                inst.gl.stop()
            except Exception as ex:
                traceback.print_exc()
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
            except NoSuchWindowException:
                try:
                    inst.driver.quit()
                except Exception as ex:
                    pass
                sleep(2)
                try:
                    inst.gl.stop()
                except Exception as glex:
                    print('GLEX: ', glex)
                break
            except Exception as ex:
                if 'chrome not reachable' in str(ex):
                    try:
                        inst.driver.quit()
                    except Exception as ex:
                        pass
                    sleep(2)
                    try:
                        inst.gl.stop()
                    except Exception as glex:
                        print('GLEX: ', glex)
                else:
                    traceback.print_exc()

    def start_facebook(self):
        fb = Facebook(self.username, self.password, self.phone_number, proxy=self.proxy,
                      gologin_id=self.gologin_profile_id)
        login_status = fb.login()
        sleep(2)
        if not login_status:
            self._add_user('Banned')
            try:
                fb.driver.quit()
                fb.gl.stop()
            except Exception as ex:
                traceback.print_exc()
            return
        self._add_user('Active')
        fb.country = self.country
        sleep(10)
        fb.get_friends_amount()
        get_user_tries = 0
        while True:
            try:
                sleep(2)
                # Get user's DB object.
                user_info = UserDB.filter_users(username=self.username, password=self.password,
                                                phone_number=self.phone_number, social_media='facebook')
                if not user_info:
                    get_user_tries += 1
                    if get_user_tries == 10:
                        self._add_user('Banned')
                        try:
                            fb.driver.quit()
                            fb.gl.stop()
                        except Exception as ex:
                            traceback.print_exc()
                        break
                    continue
                user_info = user_info[0]
                fb.usr_id = user_info['user_id']
                if fb.name is None and fb.usr_id is not None:
                    fb.get_profiles_name()
                    task = QueuedTask(FacebookProfileDB, 'update_profile', {'name': str(fb.name),
                                                                            'user_id': user_info['user_id']})
                    main_queue.put(task)
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'user_id': fb.usr_id, 'user_link': fb.user_link}))
                if fb.name == 'Name':
                    fb.get_profiles_name()
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'name': fb.name, 'user_link': fb.user_link}))
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
                        hobbies = profile['hobbies']
                        if type(hobbies) is str:
                            hobbies = hobbies.split()
                        if hobbies != 'None' and hobbies is not None:
                            fb.add_hobbies(hobbies)
                        fb.add_location(current_location, native_location)
                        fb.add_work(company, position, city, description)
                        if avatar != 'None' and avatar:
                            fb.change_pictures(avatar)
                        fb.add_bio(bio)
                    except Exception as ex:
                        traceback.print_exc()
                    task = QueuedTask(UserDB, 'update_user', {'activity': 'wait', 'status': 'done',
                                                              'user_id': user_info['user_id']})
                    main_queue.put(task)
                    sleep(3)
                elif user_info['activity'] == 'add_friends':
                    fb.add_friends(max_value=randint(3, 10))
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'user_id': user_info['user_id'], 'status': 'done',
                                                                      'activity': 'wait'}))
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
                    fb.scroll_feed(randint(1, 10))
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'user_id': user_info['user_id'], 'status': 'done',
                                                                      'activity': 'wait'}))
                res = read_json('conversations.json')
                for conv_id, conversation in res.items():
                    for post_name, post_tmp_values in conversation['tmp_data'].items():
                        index = int(post_tmp_values['index'])
                        if index >= len(post_tmp_values['full_chain']):
                            continue
                        if float(post_tmp_values['next_comment_date']) <= datetime.datetime.now().timestamp() \
                                and post_tmp_values['full_chain'][index] == fb.usr_id:
                            if fb.usr_id in conversation['meek_accs']:
                                if 'reactions' in conversation:
                                    main_queue.put(QueuedTask(UserDB, 'update_user',
                                                              {'user_id': user_info['user_id'], 'status': 'in process',
                                                               'activity': 'reactions'}))
                                    fb.make_comment(post_name, conversation['reactions'][index])
                                else:
                                    master_exist = post_tmp_values['full_chain'][:index]
                                    masters_name = []
                                    for user_id in conversation['master_accs']:
                                        try:
                                            masters_name.append(UserDB.filter_users(user_id=user_id)[0])
                                        except Exception as ex:
                                            pass
                                    for name in masters_name:
                                        try:
                                            if name['user_id'] not in master_exist:
                                                masters_name.remove(name['user_id'])
                                        except Exception as ex:
                                            print(f'MASTERS ACCOUNTS: {ex}')
                                    print("MASTERS NAMES", masters_name)
                                    print('POST NAME: ', post_name)
                                    print('ADD INFO: ', conversation['thread'][index]['text'])
                                    if masters_name:
                                        main_queue.put(QueuedTask(UserDB, 'update_user',
                                                                  {'user_id': user_info['user_id'],
                                                                   'status': 'in process',
                                                                   'activity': 'comments chain'}))
                                        fb.comments_chain(FacebookProfileDB.filter_profiles(user_id=choice(masters_name)['user_id'])[0]['name'],
                                                          conversation['thread'][index]['text'], post_name)
                                    else:
                                        print('THERE IS NO AVAILABLE MASTERS')
                            else:
                                if 'reactions' in conversation:
                                    main_queue.put(QueuedTask(UserDB, 'update_user',
                                                              {'user_id': user_info['user_id'], 'status': 'in process',
                                                               'activity': 'reactions'}))
                                    fb.make_comment(post_name, choice(conversation['reactions']))
                                else:
                                    main_queue.put(QueuedTask(UserDB, 'update_user',
                                                              {'user_id': user_info['user_id'], 'status': 'in process',
                                                               'activity': 'comments chain'}))
                                    fb.make_comment(post_name, conversation['thread'][index]['text'])
                            res[conv_id]['tmp_data'][post_name]['index'] += 1
                            dt = datetime.datetime.fromtimestamp(post_tmp_values['next_comment_date'])
                            dt += datetime.timedelta(minutes=randint(1, 5))
                            res[conv_id]['tmp_data'][post_name]['next_comment_date'] = dt.timestamp()
                            pprint(res)
                            JSONWriter('conversations.json').write_json(res)
                            main_queue.put(QueuedTask(UserDB, 'update_user',
                                                      {'user_id': user_info['user_id'], 'status': 'active',
                                                       'activity': 'wait'}))
            except NoSuchWindowException:
                try:
                    fb.driver.quit()
                except Exception as ex:
                    pass
                sleep(2)
                try:
                    fb.gl.stop()
                except Exception as glex:
                    print('GLEX: ', glex)
                self._add_user('Disconnected')
                break
            except Exception as ex:
                traceback.print_exc()
                if 'chrome not reachable' in str(ex):
                    try:
                        fb.driver.quit()
                    except Exception as ex:
                        pass
                    sleep(2)
                    try:
                        fb.gl.stop()
                    except Exception as glex:
                        print('GLEX: ', glex)
                    self._add_user('Disconnected')
                else:
                    print('WHILE THREAD: ', ex)

    def start_twitter(self):
        is_country_exist = False
        tw = Twitter(self.username, self.password, self.phone_number, self.proxy, self.country,
                     gologin_id=self.gologin_profile_id)
        login_status = tw.login()
        sleep(2)
        if not login_status:
            self._add_user('Blocked')
            try:
                tw.driver.quit()
                tw.gl.stop()
            except Exception as ex:
                traceback.print_exc()
            return
        self._add_user('Created')
        main_queue.put(QueuedTask(UserDB, 'update_user', {'user_id': tw.usr_id,
                                                          'user_link': tw.user_link}))
        tw.users_country = self.country
        get_user_tries = 0
        while True:
            try:
                sleep(1)
                # Get user's DB object.
                user_info = UserDB.filter_users(username=self.username, password=self.password,
                                                phone_number=self.phone_number, social_media='twitter')
                if not user_info:
                    get_user_tries += 1
                    if get_user_tries == 10:
                        self._add_user('Banned')
                        try:
                            tw.driver.quit()
                            tw.gl.stop()
                        except Exception as ex:
                            traceback.print_exc()
                        break
                    continue
                user_info = user_info[0]
                tw.usr_id = user_info['user_id']
                if tw.user_link is None and tw.usr_id is not None:
                    tw.get_users_link()
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'user_id': tw.usr_id,
                                                                      'user_link': tw.user_link}))
                if not is_country_exist:
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'user_id': tw.usr_id, 'country': self.country}))
                    is_country_exist = True
                if user_info['activity'] == 'fill_profile':
                    main_queue.put(QueuedTask(UserDB, 'update_user', {
                        'user_id': tw.usr_id,
                        'status': 'gardering',
                        'activity': user_info['activity']
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
                        'status': 'gardering',
                        'activity': user_info['activity'],
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
            except NoSuchWindowException:
                print('TWITTER ERROR: ')
                traceback.print_exc()
                try:
                    tw.driver.quit()
                except Exception as ex:
                    pass
                sleep(2)
                try:
                    tw.gl.stop()
                except Exception as glex:
                    print('GLEX: ', glex)
                break
            except Exception as ex:
                print('ANOTHER EXEPTION: ')
                traceback.print_exc()
                if 'chrome not reachable' in str(ex):
                    try:
                        tw.driver.quit()
                    except Exception as ex:
                        pass
                    sleep(2)
                    try:
                        tw.gl.stop()
                    except Exception as glex:
                        print('GLEX: ', glex)
                else:
                    traceback.print_exc()


if __name__ == '__main__':
    pass
