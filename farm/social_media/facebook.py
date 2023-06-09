# LOCAL
import traceback

try:
    from .base import *
    from .fb_utils import *
    from ..analyse import return_data_flair
except ImportError:
    from base import *
    from fb_utils import *
    from farm.analyse import return_data_flair

# OTHER
from random import choice


class Facebook(Base):
    def __init__(self, username, password, phone_number=None, proxy=None, gologin_id=None, country=None):
        self.xpaths = {
            'composer': "//span[contains(text(), \"What's in your mind\")]",
            'text_field': './/div[@role="button"]',
            'profile_text_box': '//div[@role="textbox"]',
            'current_location_input': '//input[@aria-label="Current city"]',
            'hometown_input': '//input[@aria-label="Hometown"]',
            'profile_svg': '//div[@aria-label="Update profile picture"]',
            'cookie_accept_btn': '//button[@data-cookiebanner="accept_button"]',
            'select_audience': '//div[@aria-label="Select audience"]',
            'bio_field': '//textarea[@aria-label="Enter bio text"]',
            'add_hobbies': '//div[@aria-label="Add hobbies" and @role="button"]',
            'edit_hobbies': '//div[@aria-label="Edit hobbies" and @role="button"]',
        }
        self.homepage = 'https://www.facebook.com/'
        super().__init__(self.homepage, proxy=proxy, gologin_id=gologin_id)
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.friends = []
        self.friends_counter = 0
        self.last_tag = None
        self.usr_id = None
        self.name = None
        self.user_link = None
        self.country = country

    def get_profiles_name(self):
        self._get_self_profile()
        self.scroll_to(y=0)
        try:
            sleep(2)
            h1_tag = self.wait(3).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'h1')))
            for h1 in h1_tag:
                if h1.text and len(h1.text) > 3:
                    self.name = h1.text
                    break
        except WebDriverException:
            pass
        self.user_link = self.driver.current_url

    def get_friends_amount(self):
        try:
            a_tags = self.wait(2).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'a')))
            for a in a_tags:
                try:
                    if 'sk=friends' in a.get_attribute('href'):
                        main_queue.put(QueuedTask(UserDB, 'update_user', {'amount_of_friends': a.text,
                                                                          'user_id': self.usr_id}))
                        return
                except Exception as ex:
                    pass

        except (WebDriverException, TimeoutException):
            pass

    def _save_new_post_to_db(self, author_name=None, text=None, img_path=None,
                             posts_link=None, date=None, likes_amount=None,
                             likes_accounts=None, comments_amount=None, comments_accounts=None, retweets_amount=None,
                             text_names=None, noun_keywords=None, label=None, sent_rate=None, lang=None, tag=None,
                             authors_link=None, authors_pic_link=None):
        args = [self.usr_id, 'facebook', author_name, text, img_path, posts_link, 'None', date, likes_amount,
                likes_accounts, comments_amount, comments_accounts, retweets_amount, text_names, noun_keywords,
                label, sent_rate, lang, tag, self.country, authors_link, authors_pic_link]
        args = replace_none(args)
        feed = QueuedTask(FeedDB, 'create_post', args)
        main_queue.put(feed)

    @staticmethod
    def _digit_in_text(text):
        for elem in text:
            if elem.isdigit():
                return True
        return False

    def _get_self_profile(self, text='profile.php'):
        if self.driver.current_url != self.homepage:
            self.open_homepage()
        try:
            a_container = self.wait(3).until(ec.presence_of_all_elements_located((By.XPATH, '//a[@href]')))
            for a in a_container:
                try:
                    if text in a.get_attribute('href'):
                        self.move_and_click(a)
                        sleep(2)
                        self.get_friends_amount()
                        return True
                except Exception as ex:
                    pass
        except WebDriverException as wde:
            pass
        return

    def _select_audience(self):
        try:
            select_audience_field = self.wait(3).until(ec.presence_of_element_located((By.XPATH,
                                                                                       self.xpaths['select_audience'])))
            public = select_audience_field.find_element(By.XPATH, './/*[contains(text(), "Public")]')
            public.click()
            done_btn = self.driver.find_element(By.XPATH, '//*[contains(text(), "Done")]')
            done_btn.click()
        except (WebDriverException, TimeoutException):
            pass

    def _change_language(self):
        for _ in range(2):
            try:
                self.driver.get(self.homepage + 'settings/?tab=language')
                main_field = self.wait(3).until(ec.presence_of_element_located((By.XPATH, '//div[@role="main"]')))
                modify_btn = main_field.find_element(By.XPATH, './/div[@role="button"]')
                self.move_and_click(modify_btn)
                sleep(1)
                combobox = self.driver.find_element(By.XPATH, '//div[@role="combobox"]')
                combobox.click()
                sleep(1)
                language = self.driver.find_element(By.XPATH, '//*[contains(text(), "English (US)")]')
                language.click()
                break
            except Exception as ex:
                pass

        main_field = self.wait(1).until(ec.presence_of_element_located((By.XPATH, '//div[@role="main"]')))
        confirm_buttons = [x for x in main_field.find_elements(By.XPATH, '//div[@role="button"]') if x.text]
        self.move_and_click(confirm_buttons[2])

    def _search(self, keyword, tab=None):
        if tab != 'groups':
            self.driver.get(self.homepage)
        try:
            search_field = self.wait(4).until(ec.presence_of_element_located((By.XPATH, '//input[@type="search"]')))
            self.move_and_click(search_field, keyword)
            sleep(4)
            options = self.wait(1).until(ec.presence_of_all_elements_located((By.XPATH, '//li[@role="option"]')))
            for option in options:
                if 'Search for' in option.text:
                    self.move_and_click(option)
                    break
            if tab:
                tab = tab.title()
                tab_btn = self.wait(5).until(ec.presence_of_element_located((By.XPATH, f'//span[contains(text(), '
                                                                                       f'"{tab}")]')))
                self.move_and_click(tab_btn)
        except WebDriverException:
            pass

    def make_comment(self, link, comment_text):
        self.driver.get(link)
        sleep(randint(8, 15))
        try:
            try:
                leave_a_comment = self.driver.find_element(By.XPATH, '//div[@aria-label="Leave a comment"]')
                self.move_and_click(leave_a_comment)
            except WebDriverException:
                pass
            self.scroll_by(y=800)
            sleep(3)
            text_box = self.driver.find_element(By.XPATH, '//div[@aria-label="Write a comment"]')
            self.move_and_click(text_box, comment_text)
            sleep(2)
            self.chain.send_keys(Keys.ESCAPE).perform()
            self.chain.reset_actions()
            try:
                submit = self.driver.find_element(By.ID, 'focused-state-composer-submit')
                self.move_and_click(submit)
            except Exception as ex:
                self.chain.send_keys(Keys.ENTER)
                self.chain.perform()
                self.chain.reset_actions()
            try:
                self.wait(3).until(ec.alert_is_present())
                alert = self.driver.switch_to.alert
                alert.dismiss()
            except (UnexpectedAlertPresentException, NoAlertPresentException):
                pass
            try:
                close_btn = self.driver.find_element(By.XPATH, '//div[@aria-label="Close"]')
                self.move_and_click(close_btn)
            except Exception as ex:
                pass
            self.open_homepage()
            return True
        except (WebDriverException, TimeoutException) as wde:
            print(wde)
        return False

    def add_location(self, current_location: str = None, native_location: str = None):
        if (not current_location and not native_location) or (current_location == 'None' and native_location == 'None'):
            return
        self._get_self_profile()
        self.driver.get(self.driver.current_url + '&sk=about_places')
        self.rs()
        buttons = self.wait(2).until(ec.presence_of_all_elements_located((By.XPATH, '//div[@role="button"]')))
        btns = [btn.text for btn in buttons if btn.text][3:]
        for btn in btns:
            self.rs()
            if 'current city' in btn.lower() and current_location:
                btn = self.driver.find_element(By.XPATH, f'//*[contains(text(), "{btn}")]')
                self.move_and_click(btn)
                self.rs()
                current_city_input = self.driver.find_element(By.XPATH, self.xpaths['current_location_input'])
                self.move_and_click(current_city_input, text=current_location)
                select_option = self.wait(1).until(ec.presence_of_element_located((By.XPATH, '//li[@role="option"]')))
                self.move_and_click(select_option)
                save_btn = self.wait(1).until(ec.presence_of_element_located((By.XPATH, '//*[contains(text(), '
                                                                                        '"Save")]')))
                self.move_and_click(save_btn)
            elif 'hometown' in btn.lower() and native_location:
                btn = self.driver.find_element(By.XPATH, f'//*[contains(text(), "{btn}")]')
                self.move_and_click(btn)
                self.rs()
                hometown_input = self.driver.find_element(By.XPATH, self.xpaths['hometown_input'])
                self.move_and_click(hometown_input, text=native_location)
                select_option = self.wait(1).until(ec.presence_of_element_located((By.XPATH, '//li[@role="option"]')))
                self.move_and_click(select_option)
                save_btn = self.wait(1).until(ec.presence_of_element_located((By.XPATH, '//*[contains(text(), '
                                                                                        '"Save")]')))
                self.move_and_click(save_btn)

    def add_hobbies(self, hobbies: list):
        hobbies = [None if elem == 'None' else elem for elem in hobbies]
        try:
            if 'profile.php' not in self.driver.current_url:
                self._get_self_profile()
            try:
                add_hobbies_btn = self.wait(5).until(ec.presence_of_element_located((By.XPATH,
                                                                                     self.xpaths['add_hobbies'])))
            except WebDriverException:
                add_hobbies_btn = self.wait(5).until(ec.presence_of_element_located((By.XPATH,
                                                                                     self.xpaths['edit_hobbies'])))
            self.move_and_click(add_hobbies_btn)
            sleep(3)
            spans = self.wait(3).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'span')))
            try:
                for span in spans:
                    if 'Search for others'.lower() in span.text.lower():
                        self.move_and_click(span)
            except WebDriverException as ex:
                pass
            for hobbie in hobbies:
                input_field = self.wait(10).until(ec.presence_of_element_located((By.XPATH,
                                                                                 '//input[@placeholder="What '
                                                                                 'do you do for fun?"]')))
                self.move_and_click(input_field)
                input_field.clear()
                sleep(1)
                self.move_and_click(input_field, text=hobbie)
                options = self.wait(3).until(ec.presence_of_all_elements_located((By.XPATH, '//li[@role="option"'
                                                                                            ' and @aria-selected="false"]')))
                self.move_and_click(options[0])
            sleep(2)
            spans = self.wait(2).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'span')))
            for span in spans:
                if 'save' in span.text.lower():
                    try:
                        self.move_and_click(span)
                        break
                    except StaleElementReferenceException:
                        pass
        except (WebDriverException, TimeoutException) as err:
            print('ERR: ', err)

    def scroll_feed(self, minutes: float | int):
        end_time = datetime.datetime.now() + timedelta(minutes=minutes)
        article = self.wait(3).until(ec.presence_of_element_located((By.XPATH, '//div[@role="article"]')))
        self.move_and_click(element=article, to_click=False)
        while True:
            if self.driver.current_url != self.homepage:
                self.open_homepage()
            if datetime.datetime.now() >= end_time:
                return
            direction = choice(['Down', 'Up'])
            self.rs()
            if direction == 'Down':
                self.scroll_by(y=randint(200, 1300))
            else:
                self.scroll_by(y=randint(-1300, 200))

    def collect_posts(self, tag='News', amount=15):
        try:
            result, data_debug, people = parsing_posts(tag, amount, self.driver, 0, data_debug={
                'exceptions': '',
                'tracebacks': '',
                'error_number': 0
            })
            for res in result:
                text = res.get('text')
                user = res.get('account')
                user_link = res.get('account_link')
                posts_pubdate = res.get('date')
                likes_amount = res.get('likes')
                comments_amount = res.get('comments')
                shares_amount = res.get('shares')
                users_profile_pic = res.get('link')
                self._save_new_post_to_db(user, text, None, user_link, posts_pubdate, likes_amount, [],
                                          comments_amount, [], shares_amount, *return_data_flair(text)[1:], tag,
                                          user_link, users_profile_pic)
        except Exception as ex:
            print('EX: ' * 50, ex)

    def add_work(self, company=None, position=None, city=None, description=None):
        work_info = [company, position, city, description]
        work_info = [None if elem == 'None' else elem for elem in work_info]
        if not any(work_info):
            return
        self._get_self_profile()
        self.rs()
        self.driver.get(self.driver.current_url + '&sk=about_work_and_education')
        self.rs()
        try:
            workplace = self.driver.find_element(By.XPATH, '//*[contains(text(), "Add a workplace")]')
            self.move_and_click(workplace)
            sleep(2)
            fields = self.wait(2).until(ec.presence_of_all_elements_located((By.XPATH, '//*[@role="combobox"]')))[1:4]
            textarea = self.driver.find_element(By.TAG_NAME, 'textarea')
            fields += [textarea]
            for index, field in enumerate(fields):
                if work_info[index]:
                    self.chain.send_keys(Keys.ESCAPE).perform()
                    self.chain.reset_actions()
                    self.move_and_click(field, work_info[index])
        except (TimeoutException, WebDriverException) as exception:
            print(exception)
        submit = self.wait(1).until(ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "Save")]')))
        self.move_and_click(submit)

    def add_bio(self, text=None):
        try:
            self._get_self_profile()
            add_btns = ['Add bio', 'Edit bio']
            for btn in add_btns:
                try:
                    add_bio_btn = self.wait(3).until(ec.presence_of_element_located((By.XPATH,
                                                                                     f'//div[@aria-label="{btn}"]')))
                    self.scroll_into_view(add_bio_btn)
                    self.move_and_click(add_bio_btn)
                except TimeoutException:
                    pass
            textareas = self.wait(3).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'textarea')))
            for textarea in textareas:
                if textarea.get_attribute('aria-label') == 'Enter bio text':
                    self.move_and_click(textarea, text)
                    # self.driver.execute_script("var ele=arguments[0]; ele.innerHTML = 'Google';", textarea)
            save_btn = self.driver.find_element(By.XPATH, '//span[contains(text(), "Save")]')
            self.scroll_into_view(save_btn)
            self.move_and_click(save_btn)
            sleep(3)
            try:
                skip_btn = self.driver.find_element(By.XPATH, '//span[contains(text(), "Skip")]')
                skip_btn.click()
            except WebDriverException:
                pass
            sleep(5)
            return True
        except (TimeoutException, WebDriverException):
            return False

    def change_pictures(self, avatar: str = None):
        if not avatar or avatar == 'None':
            return
        self._get_self_profile()
        profile_logo = self.wait(5).until(ec.presence_of_element_located((By.XPATH, self.xpaths['profile_svg'])))
        self.move_and_click(profile_logo)

        self.rs()
        upload_photo_text = self.driver.find_element(By.XPATH, '//span[contains(text(), "Upload photo")]')
        inp = upload_photo_text.find_element(By.XPATH, '..')
        for _ in range(10):
            try:
                inp_field = inp.find_element(By.XPATH, './/input[@type="file"]')
                inp_field.send_keys(IMG_DIR + 'facebook/' + avatar)
                sleep(1)
                break
            except WebDriverException as wde:
                print('PROFILE PIC WDE')
                inp = inp.find_element(By.XPATH, '..')
        sleep(10)
        try:
            close = self.wait(4).until(ec.presence_of_element_located((By.XPATH, '//span[contains(text(), "Close")]')))
            self.move_and_click(close)
        except (WebDriverException, TimeoutException):
            pass
        save = self.wait(4).until(ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "Save")]')))
        self.move_and_click(save)
        sleep(7)

    def accept_cookies(self):
        try:
            btn = self.wait(10).until(ec.presence_of_element_located((By.XPATH, self.xpaths['cookie_accept_btn'])))
            self.move_and_click(btn)
        except WebDriverException as wde:
            print(wde)

    def login(self) -> bool:
        self.open_homepage()
        self.accept_cookies()
        try:
            self.wait(3).until(ec.presence_of_element_located((By.XPATH,
                                                               '//button[@data-testid="royal_login_button"]')))
        except Exception as ex:
            self._change_language()
            return True
        for _ in range(2):
            try:
                email_field = self.wait(3).until(ec.presence_of_element_located((By.ID, 'email')))
                self.move_and_click(email_field, self.username)
                self.rs()

                pass_field = self.wait(3).until(ec.presence_of_element_located((By.ID, 'pass')))
                self.move_and_click(pass_field, self.password)

                self.rs()
                login_btn = self.driver.find_element(By.NAME, 'login')
                self.move_and_click(login_btn)
                sleep(2)
                try:
                    divs = self.wait(3).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'div')))
                    for div in divs:
                        if 'access denied' in div.text.lower():
                            return False
                        if 'mobile number' in div.text.lower():
                            return False
                except WebDriverException:
                    pass
                self._change_language()
                try:
                    for btn in self.driver.find_elements(By.TAG_NAME, 'div'):
                        if 'You must confirm your password to edit your account settings.' in btn.text:
                            return False
                except Exception as ex:
                    pass
                return True
            except WebDriverException as wde:
                print(wde)
            except Exception as ex:
                pass
        return False

    def get_exact_users_friends(self, profile_link: str = None, limit=100):
        if 'www.facebook.com' in profile_link:
            self.driver.get(profile_link)
            self.rs()
            friends_btn = self.wait(3).until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'friends')))
            self.move_and_click(friends_btn)
            self.rs()
            while len(self.friends) <= limit:
                self.scroll_to_the_end()
                a_container = self.driver.find_elements(By.TAG_NAME, 'a')
                for a in a_container:
                    try:
                        href = str(a.get_attribute('href'))
                        if 'profile.php' in href and href not in self.friends:
                            self.friends.append(href)
                    except Exception as ex:
                        print(ex)
            print('END')

    def add_friends(self, max_value=100):
        tmp_url = 'https://www.facebook.com/friends/suggestions'
        self.driver.get(tmp_url)
        sleep(3)
        while self.friends_counter <= max_value:
            self.rs()
            body = self.driver.find_element(By.TAG_NAME, 'body')
            if "When you have friend requests or suggestions, you'll see them here." in body.text:
                break
            try:
                add_friend_btn = self.wait(3).until(ec.presence_of_element_located((By.XPATH,
                                                                                    '//*[contains(text(), '
                                                                                    '"Add Friend")]')))
            except WebDriverException as wde:
                self.driver.refresh()
                continue
            try:
                self.scroll_into_view(add_friend_btn)
            except StaleElementReferenceException as sere:
                print('SERE:', sere)
            self.rs()
            try:
                self.move_and_click(add_friend_btn)
            except WebDriverException as wde:
                print(wde)
                self.driver.refresh()

    def make_post(self, text=None, filename=None):
        self._get_self_profile()
        self.wait_until_profile_loads(5, 2, 'profile.php')
        sleep(4)
        try:
            spans = self.driver.find_elements(By.TAG_NAME, 'span')
            for span in spans:
                print(span.text)
                if "What's on your mind?" in span.text:
                    self.move_and_click(span)
                    sleep(4)
            self.rs()
            self._select_audience()
            sleep(3)
            textbox = self.driver.find_element(By.XPATH, self.xpaths['profile_text_box'])
            self.move_and_click(textbox, text)
            if filename and filename != 'None':
                photo_video = self.driver.find_element(By.XPATH, '//div[@aria-label="Photo/video"]')
                self.move_and_click(photo_video)
                sleep(1)
                get_form = self.wait(2).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'input')))
                for form in get_form:
                    if str(form.get_attribute('accept')) == \
                            'image/*,image/heif,image/heic,video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv':
                        form.send_keys(IMG_DIR + 'facebook/' + filename)
            sleep(7)
            post = self.driver.find_element(By.XPATH, '//div[@aria-label="Post"]')
            post.click()
        except WebDriverException as wde:
            print('MAKE POST WDE: ', wde)

    def explore_platform(self):
        pass

    def join_groups_by_interests(self, tag: str, *args):
        max_amount_of_groups = randint(3, 7)
        self.driver.get('https://www.facebook.com/groups/feed/')
        sleep(3)
        self._search(tag, tab='groups')
        join_buttons = self.wait(4).until(ec.presence_of_all_elements_located((By.XPATH, '//span[contains(text(), '
                                                                                         '"Join")]')))
        for index, join_btn in enumerate(join_buttons):
            if index == max_amount_of_groups:
                break
            self.move_and_click(join_btn)
            try:
                close_btn = self.wait(1).until(ec.presence_of_element_located((By.XPATH, '//*[@aria-label="Close"]')))
                close_btn.click()
            except (TimeoutException, WebDriverException):
                pass

    def comments_chain(self, masters_name: str, text: str, link: str):
        last_page_height = 0
        if self.driver.current_url != link:
            self.driver.get(link)
        sleep(2)
        try:
            show_all_btn = self.wait(2).until(ec.presence_of_element_located((By.XPATH,
                                                                              '//div[@aria-label="See All" '
                                                                              'and @role="button"]')))
            self.move_and_click(show_all_btn)
        except Exception as ex:
            pass
        sleep(2)
        while True:
            self.scroll_by(y=1200)
            try:
                buttons = self.wait(2).until(ec.presence_of_all_elements_located((By.XPATH, '//div[@role="button"]')))
                for btn in buttons:
                    if 'more comments' in btn.text:
                        self.scroll_into_view(btn)
                        self.move_and_click(btn)
                        sleep(2)
                        break
            except Exception as ex:
                print(ex)
            try:
                articles = self.driver.find_elements(By.XPATH, '//div[@aria-label]')
                for article in articles:
                    if f'Comment by {masters_name}' in article.get_attribute('aria-label'):
                        print(article.get_attribute('aria-label'))
                        reply_button = article.find_element(By.XPATH, './/div[contains(text(), "Reply")]')
                        print(reply_button.text)
                        try:
                            self.scroll_into_view(reply_button)
                            self.scroll_by(y=-500)
                        except Exception as ex:
                            pass
                        self.move_and_click(reply_button)
                        sleep(3)
                        self.chain.send_keys(text)
                        self.chain.perform()
                        self.chain.reset_actions()
                        sleep(3)
                        self.chain.send_keys(Keys.ESCAPE)
                        self.chain.perform()
                        self.chain.reset_actions()
                        sleep(2)
                        self.chain.send_keys(Keys.ENTER)
                        self.chain.perform()
                        self.chain.reset_actions()
                        return True
            except (WebDriverException, TimeoutException) as wde:
                traceback.print_exc()
                print(wde)
            except Exception as ex:
                traceback.print_exc()
            if last_page_height == int(self.driver.execute_script('return document.body.scrollHeight')):
                return False
            last_page_height = int(self.driver.execute_script('return document.body.scrollHeight'))


if __name__ == '__main__':
    f = Facebook('+33783473178', 'cBtue9fa5uTtZpx')
    f.login()
    f.add_hobbies(['games', 'music'])
    # f.make_post("Just test text.", '/home/penguin_nube/Pictures/Screenshot_20230313_020220.png')
