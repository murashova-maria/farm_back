# LOCAL
import logging

try:
    from .base import *
    from ..analyse import return_data_flair
except ImportError:
    from base import *
    from farm.analyse import return_data_flair


class Instagram(Base):
    def __init__(self, username, password, phone_number=None, proxy=None):
        self.long_xpaths = {
            'add_image_to_the_publication': '//input[accept="image/jpeg,image/png,image/heic,'
                                            'image/heif,video/mp4,video/quicktime"]',
        }
        homepage = 'https://www.instagram.com'
        super().__init__(homepage, proxy)
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.chain = ActionChains(self.driver)
        self.xpath_template = lambda x, elem='*': f'//{elem}[contains(text(), "{x}")]'
        self.execution_status = str()
        self.usr_id = 0
        self.last_tag = ''
        self.step = ''

    def _liked_users(self, post_url):
        pass

    def _commented_users(self, post_url):
        pass

    def _save_new_post_to_db(self, author_name, text, img_path, posts_link, date, likes_amount, likes_accounts,
                             comments_amount, comments_accounts, retweets_amount, text_names, noun_keywords,
                             label, sent_rate, lang):
        args = [self.usr_id, 'instagram', author_name, text, img_path, posts_link, 'None', date, likes_amount,
                likes_accounts, comments_amount, comments_accounts, retweets_amount, text_names, noun_keywords,
                label, sent_rate, lang]
        feed = QueuedTask(FeedDB, 'create_post', args)
        main_queue.put(feed)

    def _allow_cookies(self) -> None:
        text = 'Allow essential and optional cookies'
        xpath = self.xpath_template(text)
        while True:
            try:
                cookies_alert = self.wait(5).until(ec.presence_of_element_located((By.XPATH, xpath)))
                if not self.execution_status:
                    cookies_alert.click()
                    self.execution_status = '[FIRST STEP]: PASSED'
            except WebDriverException:
                break

    def _decline_saving_login_data(self) -> None:
        xpath = self.xpath_template('Not Now', 'div')
        try:
            decline_btn = self.wait(5).until(ec.presence_of_element_located((By.XPATH, xpath)))
            self.move_and_click(decline_btn)
        except WebDriverException as wde:
            input(f'{wde} ::: >>> ')

    def _wait_until_homepage_load(self) -> bool:
        for _ in range(20):
            sleep(1)
            try:
                divs = self.driver.find_elements(By.TAG_NAME, 'div')
                for div in divs:
                    if 'profile' == div.text.lower():
                        return True
            except WebDriverException:
                pass
        return False

    def _open_from_navbar(self, tag=None):
        if not tag:
            return
        try:
            create_btn_xpath = self.xpath_template(tag.title(), 'div')
            create_btn = self.wait(5).until(ec.presence_of_element_located((By.XPATH, create_btn_xpath)))
            create_btn.click()
            self.rs()
        except TimeoutException:
            pass

    def _edit_profile(self):
        try:
            self._open_from_navbar('profile')
            edit_profile = self.wait(3).until(ec.presence_of_element_located((By.XPATH,
                                                                              '//a[@href="/accounts/edit/"]')))
            self.move_and_click(edit_profile)
            self.rs()
        except TimeoutException:
            return False
        return True

    def _select_gender(self, gender):
        if not gender:
            return
        try:
            choose_gender = self.driver.find_element(By.ID, 'pepGender')
            self.move_and_click(choose_gender)
            if gender.lower() == 'male':
                value = '1'
            else:
                value = '2'
            genders = self.wait(2).until(ec.presence_of_all_elements_located((By.XPATH, '//input[@name="gender"]')))
            for gender_field in genders:
                if value == gender_field.get_attribute('value'):
                    gender_field.click()
                    done_btn = self.wait(3).until(ec.presence_of_element_located((By.XPATH, '//button[contains(text(), '
                                                                                            '"Done")]')))
                    self.move_and_click(done_btn)
                    break
        except (WebDriverException, TimeoutException):
            pass

    def _select_avatar(self, avatar):
        if not avatar:
            return
        try:
            self.rs()
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            inputs[0].send_keys(avatar)
        except WebDriverException:
            pass

    def _set_like(self):
        pass

    def login(self) -> bool:
        self.open_homepage()
        self._allow_cookies()
        try:
            login_data = [self.username, self.password]
            input_fields = self.wait(2).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'input')))
            for index, ld in enumerate(login_data):
                field = input_fields[index]
                field.click()
                field.send_keys(ld)
            sleep(2)
            login_btn = self.driver.find_element(By.XPATH, '//*[contains(text(), "Log in")]')
            login_btn.click()
            self._wait_until_homepage_load()
            self._decline_saving_login_data()
            return True
        except (WebDriverException, TimeoutException) as wte:
            return False

    def make_post(self, text=None, filename=None) -> bool:
        try:
            self._open_from_navbar('Create')
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            inputs[1].send_keys(filename)
            for _ in range(2):
                self.rs()
                next_btn = self.driver.find_element(By.XPATH, self.xpath_template('Next', 'div'))
                self.move_and_click(next_btn)
            self.rs()
            if text:
                text_field = self.driver.find_element(By.XPATH, '//div[@aria-label="Write a caption..."]')
                self.move_and_click(text_field, text)
            next_btn = self.driver.find_element(By.XPATH, self.xpath_template('Share', 'div'))
            self.move_and_click(next_btn)
            self.driver.refresh()
            return True
        except WebDriverException as wde:
            print(wde.msg)
        return False

    def fill_profile(self, name=None, username=None, bio=None, gender=None, avatar=None):
        input_fields = {
            'pepName': name,
            'pepUsername': username,
            'pepBio': bio
        }
        if not self._edit_profile():
            return False
        try:
            for key, value in input_fields.items():
                if not value:
                    continue
                field = self.wait(3).until(ec.presence_of_element_located((By.ID, key)))
                try:
                    field.clear()
                except Exception as ex:
                    pass
                field.send_keys(value)
            self._select_gender(gender)
            sleep(6)
            self._select_avatar(avatar)
            submit = self.driver.find_element(By.XPATH, '//div[contains(text(), "Submit")]')
            self.move_and_click(submit)
            sleep(3)
            self.open_homepage()
            return True
        except (TimeoutException, WebDriverException) as wde:
            pass
            # logging.error(f'[ERROR]: Filling profile.\nError text: {wde}')
        return False

    def collect_posts(self, tag=None):
        if self.driver.current_url != 'https://www.instagram.com/':
            self.open_homepage()
        self.scroll_to_the_end()
        sleep(5)
        articles = self.wait(2).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'article')))
        try:
            for article in articles:
                a_tags = article.find_elements(By.TAG_NAME, 'a')
                posts_link = [a.get_attribute('href')[:a.get_attribute('href').find('liked_by')] for a in a_tags
                              if 'liked_by' in a.get_attribute('href')][0]
                img_path = article.find_elements(By.XPATH, './/img[@src and @crossorigin="anonymous"]')
                sections = article.find_elements(By.TAG_NAME, 'section')
                authors_text = article.find_element(By.TAG_NAME, 'h1').text
                authors_username = [a.text for a in a_tags
                                    if 'explore' not in a.get_attribute('href') and 'Learn more' not in a.text
                                    and a.text != ''][0]
                likes_amount = [elem.text[:elem.text.find('likes')] for elem in sections if 'likes' in elem.text]
                comments_amount = [a.text for a in a_tags
                                   if 'comments' in a.get_attribute('href')]
                if len(img_path) == 1:
                    img_path = None
                else:
                    img_path = img_path[-1].get_attribute('src')
                if len(likes_amount) >= 1:
                    likes_amount = likes_amount[0]
                else:
                    likes_amount = None
                rate = return_data_flair(authors_text)[1:]
                data = [authors_username, authors_text, img_path, posts_link, datetime.now(), likes_amount,
                        None, comments_amount, None, None, *rate]
                # self._save_new_post_to_db(author_name=authors_username, text=authors_text,
                #                           img_path=img_path, posts_link=posts_link, date=datetime.now(),
                #                           likes_amount=likes_amount, comments_amount=comments_amount,
                #                           retweets_amount=None, likes_accounts=None, comments_accounts=None, *rate)
                self._save_new_post_to_db(*data)

        except StaleElementReferenceException as sere:
            pass
            # logging.warning(f'[ERROR]: Scrolling instagram feed. \nError text: {sere}')


if __name__ == '__main__':
    pass
