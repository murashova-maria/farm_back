# LOCAL
try:
    from .base import *
    from ..analyse import return_data_flair
except ImportError as ie:
    from base import *
    from farm.analyse import return_data_flair


class Twitter(Base):
    def __init__(self, username, password, phone_number=None, proxy=None):
        # Dict with all xpath. It was created to avoid PEP808 attention number's E501
        self.xpaths = {
            'login': '//span[text()="Log in"]',
            'username': '//input[@autocomplete="username"]',
            'password': '//input[@name="password"]',
            'next_btn': '//span[text()="Next"]',
            'login_btn': '//div[@data-testid="LoginForm_Login_Button"]',
            'tweet_btn': '//a[@href="/compose/tweet"]',
            'image_path': '//input[@accept]',
            'tweet_it': '//div[@data-testid="tweetButton"]',

            'explore': '//a[@href="/explore"]',
            'search_field': '//input[@data-testid="SearchBox_Search_Input"]',
            'article': '//article[@role="article"]',
            'tweet_text': './/div[@data-testid="tweetText"]',
            'username_articles_row': './/*[@data-testid="User-Name"]',
            'image_xpath': './/*[@data-testid="tweetPhoto"]',
            'apply_img': '//div[@data-testid="applyButton"]',
            'select_avatar_next_btn': '//div[@data-testid="ocfSelectAvatarNextButton"]',
            'select_cover_next_btn': '//div[@data-testid="ocfSelectBannerNextButton"]',
            'tmp_bio': '//textarea[@data-testid="ocfEnterTextTextInput"]',
            'confirm_tmp_bio': '//div[@data-testid="ocfEnterTextNextButton"]',
            'skip_avatar_for_now': ['//div[@data-testid="ocfSelectAvatarSkipForNowButton"]',
                                    '//div[@data-testid="ocfSelectBannerSkipForNowButton"]',
                                    '//div[@data-testid="ocfEnterTextSkipForNowButton"]',
                                    '//div[@data-testid="ocfEnterTextSkipForNowButton"]'],

            'get_profile': '//*[@data-testid="AppTabBar_Profile_Link"]',
            'set_the_profile': '//a[@data-testid="editProfileButton"]',
            'skip_img': '//div[@data-testid="ocfSelectBannerSkipForNowButton"]',
            'file_input': '//input[@data-testid="fileInput"]',
            'change_profile_label': '//div[@aria-labelledby="modal-header"]',
            'save_profile': '//div[@data-testid="Profile_Save_Button"]',
        }
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.homepage = 'https://twitter.com/'
        super().__init__(self.homepage, proxy=proxy)
        self.home = self.homepage + 'home'
        self.chain = ActionChains(self.driver)
        self.scroll_height = 0
        self.repetitions_counter = 0
        self.last_post = ''
        self.usr_id = None

    def handle_correct_window(self):
        pass

    def _is_account_suspended(self):
        try:
            self.wait(2).until(ec.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Account suspended')]")))
            for user in UserDB.filter_users(username=self.username):
                if user['social_media'] == 'twitter':
                    data = {'user_id': self.usr_id, 'status': 'suspended'}
                    suspended = QueuedTask(UserDB, 'update_user', data)
                    main_queue.put(suspended)
        except WebDriverException:
            pass

    def _save_new_post_to_db(self, author_name, text, img_path, posts_link, date, likes_amount, likes_accounts,
                             comments_amount, comments_accounts, retweets_amount, text_names, noun_keywords,
                             label, sent_rate, lang):
        args = [self.usr_id, 'twitter', author_name, text, img_path, posts_link, 'None', date, likes_amount,
                likes_accounts, comments_amount, comments_accounts, retweets_amount, text_names, noun_keywords,
                label, sent_rate, lang]
        feed = QueuedTask(FeedDB, 'create_post', args)
        main_queue.put(feed)

    def _accept_cookies(self):
        spans = self.wait(3).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'span')))
        for span in spans:
            try:
                if span.text == 'Accept all cookies':
                    span.click()
                    return
            except Exception as ex:
                pass

    def _handle_login_errors(self):
        # Try to close or avoid all banners with errors.
        sleep(2)
        xpaths = {
            'unusual_activity': '//span[contains(text(), "There was unusual login activity on your account. ' 
                                'To help keep your account safe, '
                                'please enter your phone number or username to verify it’s you.")]',
        }
        for key, value in xpaths.items():
            try:
                error_msg = self.driver.find_element(By.XPATH, value)
                if error_msg.text and key == 'unusual_activity' and self.phone_number:
                    # Enter phone number if it is necessary.
                    input_field = self.driver.find_element(By.TAG_NAME, 'input')
                    input_field.click()
                    input_field.send_keys(self.phone_number)

                    next_btn = self.driver.find_element(By.XPATH, self.xpaths['next_btn'])
                    next_btn.click()
            except WebDriverException as wde:
                print('ERRORS:', wde)

    def _get_profile(self):
        app_tab_bar = self.wait(3).until(ec.presence_of_element_located((By.XPATH, self.xpaths['get_profile'])))
        self.chain.reset_actions()
        self.chain.move_to_element(app_tab_bar)
        self.rs()
        self.chain.click()
        self.chain.perform()
        self.chain.reset_actions()
        self._is_account_suspended()

    def review(self, tag: str):
        # Open 'review' or 'search' field to start search.
        if self.driver.current_url != self.home:
            self.open_homepage()
        self._is_account_suspended()
        try:
            review_btn = self.wait(3).until(ec.presence_of_element_located((By.XPATH, self.xpaths['explore'])))
            review_btn.click()

            search_box = self.wait(3).until(ec.presence_of_element_located((By.XPATH, self.xpaths['search_field'])))
            search_box.click()
            search_box.send_keys(tag + Keys.ENTER)
            return True
        except WebDriverException:
            pass
        return False

    def _update_profiles_header(self, input_data: list, textarea_data: list):
        try:
            change_box = self.driver.find_element(By.XPATH, self.xpaths['change_profile_label'])
            input_fields = change_box.find_elements(By.TAG_NAME, 'input')
            for index in range(4):
                if input_data[index]:
                    if input_fields[index].get_attribute('type') == 'file':
                        if '/' not in input_data[index]:
                            continue
                        input_fields[index].send_keys(input_data[index])
                        apply_btn = self.wait(2).until(ec.presence_of_element_located((By.XPATH, self.xpaths['apply_img'])))
                        self.move_and_click(apply_btn)
                        sleep(2)
                        input_fields = change_box.find_elements(By.TAG_NAME, 'input')
                    else:
                        input_fields[index].clear()
                        self.move_and_click(element=input_fields[index], text=input_data[index])
            self.rs()
            textareas = change_box.find_elements(By.TAG_NAME, 'textarea')
            for index, textarea in enumerate(textareas):
                try:
                    if textarea_data[index]:
                        textarea.clear()
                        self.move_and_click(textarea, textarea_data[index])
                except WebDriverException:
                    pass
            self.rs()
            change_box = self.driver.find_element(By.XPATH, self.xpaths['change_profile_label'])
            save_btn = change_box.find_element(By.XPATH, self.xpaths['save_profile'])
            self.move_and_click(save_btn)
        except WebDriverException as wde:
            print(wde)

    def _fill_profiles_header(self, input_data: list, textarea_data: list):
        for i in range(4):
            change_box = self.driver.find_element(By.XPATH, self.xpaths['change_profile_label'])
            if 'Pick a profile picture' in change_box.text and input_data[1]:
                file_input = change_box.find_element(By.XPATH, './/input[@data-testid="fileInput"]')
                file_input.send_keys(input_data[1])
                sleep(2)
                apply = self.driver.find_element(By.XPATH, self.xpaths['apply_img'])
                self.move_and_click(apply)

                next_btn = self.driver.find_element(By.XPATH, self.xpaths['select_avatar_next_btn'])
                self.move_and_click(next_btn)
            elif 'Pick a header' in change_box.text and input_data[0]:
                file_input = change_box.find_element(By.XPATH, './/input[@data-testid="fileInput"]')
                file_input.send_keys(input_data[0])
                sleep(2)
                apply = self.driver.find_element(By.XPATH, self.xpaths['apply_img'])
                self.move_and_click(apply)
                sleep(2)
                next_btn = self.driver.find_element(By.XPATH, self.xpaths['select_cover_next_btn'])
                self.move_and_click(next_btn)
            elif 'Describe yourself' in change_box.text and textarea_data[0]:
                bio_field = change_box.find_element(By.XPATH, self.xpaths['tmp_bio'])
                self.move_and_click(bio_field, textarea_data[0])
                confirm = self.driver.find_element(By.XPATH, self.xpaths['confirm_tmp_bio'])
                self.move_and_click(confirm)
            else:
                skip_btns = self.driver.find_elements(By.XPATH, '//div[@data-testid]')
                for skip in skip_btns:
                    if 'SkipForNow' in skip.get_attribute('data-testid'):
                        self.move_and_click(skip)

    def login(self) -> bool:
        self.open_homepage()
        self._is_account_suspended()
        try:
            self._accept_cookies()
            try:
                login_btn = self.wait(3).until(ec.presence_of_element_located((By.XPATH, self.xpaths['login'])))
                self.move_and_click(login_btn)
            except (WebDriverException, TimeoutException):
                login_btn = self.wait(3).until(ec.presence_of_element_located((By.XPATH,
                                                                               '//a[@data-testid="loginButton"]')))
                self.move_and_click(login_btn)
            self.rs()

            username_field = self.wait(5).until(ec.presence_of_element_located((By.XPATH, self.xpaths['username'])))
            username_field.click()
            self.rs()
            username_field.send_keys(self.username)

            next_btn = self.driver.find_element(By.XPATH, self.xpaths['next_btn'])
            next_btn.click()

            self._handle_login_errors()

            self.rs()
            password_field = self.wait(3).until(ec.presence_of_element_located((By.XPATH, self.xpaths['password'])))
            password_field.click()
            password_field.send_keys(self.password)
            sleep(3)

            log_in_btn = self.driver.find_element(By.XPATH, self.xpaths['login_btn'])
            log_in_btn.click()
            sleep(5)
            if self.driver.current_url == self.home:
                return True
        except (WebDriverException, NoSuchWindowException) as wde:
            print('LOGIN:', wde)
        return False

    def fill_profiles_header(self, avatar=None, cover=None, name=None, about_myself=None, location=None):
        self._get_profile()
        text_fields = [about_myself]
        image_fields = [cover, avatar, name, location]
        set_the_profile = self.wait(5).until(ec.presence_of_element_located((By.XPATH, self.xpaths['set_the_profile'])))
        set_the_profile.click()
        self.rs()
        change_box = self.driver.find_element(By.XPATH, self.xpaths['change_profile_label'])
        # If 'pick' text is exist when we try to open and fill our profile - it means that the profile wasn't filled up.
        # If there is no 'pick' - update current values.
        if 'pick' in change_box.text.lower():
            self._fill_profiles_header(image_fields, text_fields)
        else:
            self._update_profiles_header(image_fields, text_fields)

    def make_post(self, text: None | str = None, filename: None | str = None):
        # If there is nothing to post - cancel.
        if not text and not filename or text == 'None' and filename == 'None':
            return
        if self.driver.current_url != self.home:
            self.open_homepage()
        # Select and click 'tweet' button
        tweet_btn = self.wait(3).until(ec.presence_of_element_located((By.XPATH, self.xpaths['tweet_btn'])))
        tweet_btn.click()
        # Here we use ActionChains, because Twitter doesn't have input field for that place in its HTML code.
        if text:
            self.chain.reset_actions()
            self.chain.send_keys(text).perform()

        if filename:  # Paste image if it exists.
            image_path = self.driver.find_element(By.XPATH, self.xpaths['image_path'])
            image_path.send_keys(filename)
        tweet_it = self.driver.find_element(By.XPATH, self.xpaths['tweet_it'])
        tweet_it.click()

    def collect_posts(self, tag='#News'):
        if 'search' not in self.driver.current_url:
            self.review(tag)
        if not self.scroll_height:
            self.scroll_height = self.driver.execute_script('return document.documentElement.scrollHeight')
        self.scroll_by(0, int(self.scroll_height)*2)
        sleep(1)
        articles = self.wait(3).until(ec.presence_of_all_elements_located((By.XPATH, self.xpaths['article'])))
        if articles[-1].text == self.last_post:
            self.repetitions_counter += 1
        self.last_post = articles[-1].text

        if self.repetitions_counter == 5:
            # Change 'latest' tab to general news if there is no posts anymore.
            self.driver.get(self.driver.current_url + '&f=live')
            return
        for article in articles:
            try:
                posts_link = None
                pic_link = None
                article_text = article.find_element(By.XPATH, self.xpaths['tweet_text']).text
                rate = return_data_flair(article_text)[1:]
                username_field = article.find_element(By.XPATH, self.xpaths['username_articles_row'])
                username = username_field.find_element(By.XPATH, './/a[@href]').get_attribute('href')
                try:
                    pic = article.find_element(By.XPATH, self.xpaths['image_xpath'])
                    pic_link = pic.find_element(By.TAG_NAME, 'img').get_attribute('src')
                except WebDriverException:
                    pass
                links = article.find_elements(By.XPATH, './/a[@role="link"]')
                for link in links:
                    link = link.get_attribute('href')
                    if 'status' in link:
                        posts_link = link
                        break
                likes = article.find_element(By.XPATH, './/*[@data-testid="like"]').text
                replies = article.find_element(By.XPATH, './/*[@data-testid="reply"]').text
                retweets = article.find_element(By.XPATH, './/*[@data-testid="retweet"]').text
                self._save_new_post_to_db(username, article_text, pic_link, posts_link, datetime.now(), likes, [],
                                          replies, [],
                                          retweets, *rate)
            except Exception as ex:
                print(ex)


if __name__ == '__main__':
    pass
