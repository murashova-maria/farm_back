# LOCAL
import datetime
import logging

try:
    from .base import *
    from ..analyse import return_data_flair
except ImportError:
    from base import *
    from farm.analyse import return_data_flair
import instagrapi
from bs4 import BeautifulSoup


class Instagram(Base):
    def __init__(self, username, password, phone_number=None, proxy=None):
        self.client = None
        # try:
        #     self.client = instagrapi.Client()
        #     if proxy and proxy != 'None':
        #         self.client.set_proxy(f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["password"]}')
        #     self.client.login(username, password)
        # except Exception:
        #     self.client = None
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

    def _liked_and_commented_users(self, post_url) -> dict:
        try:
            comments = []
            likes = []
            if self.client is None:
                return {'comments': [], 'likes': []}
            media_pk = self.client.media_pk_from_url(post_url)
            likers = self.client.media_likers(media_pk)
            commenters = self.client.media_comments(media_pk)
            for comment in commenters:
                # comments.append({'text': comment.text, 'date': comment.created_at_utc, 'likes': comment.like_count,
                #                  'creator': comment.user.username})
                comments.append([comment.text, comment.created_at_utc, comment.like_count, comment.user.username])
            for like in likers:
                likes.append([like.username, str(like.profile_pic_url)])
            return {'comments': comments, 'likes': likes}
        except Exception as ex:
            pass
            # if 'login_required' in str(ex).lower():
            #     self.client.relogin()
            #     sleep(3)
        return {'comments': [], 'likes': []}

    def _save_new_post_to_db(self, author_name, text, img_path, posts_link, date, likes_amount, likes_accounts,
                             comments_amount, comments_accounts, retweets_amount, text_names, noun_keywords,
                             label, sent_rate, lang, tag):
        args = [self.usr_id, 'instagram', author_name, text, img_path, posts_link, 'None', date, likes_amount,
                likes_accounts, comments_amount, comments_accounts, retweets_amount, text_names, noun_keywords,
                label, sent_rate, lang, tag]
        args = replace_none(args)
        feed = QueuedTask(FeedDB, 'create_post', args)
        main_queue.put(feed)

    def _allow_cookies_v2(self):
        try:
            sleep(5)
            text = 'Allow all cookies'
            buttons = self.wait(3).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'button')))
            for button in buttons:
                if text.lower() in button.text.lower():
                    self.move_and_click(button)
                    break
        except Exception as ex:
            pass
        sleep(4)

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
        self._allow_cookies_v2()

    def _decline_saving_login_data(self) -> None:
        xpath = self.xpath_template('Not Now', 'div')
        try:
            decline_btn = self.wait(5).until(ec.presence_of_element_located((By.XPATH, xpath)))
            self.move_and_click(decline_btn)
        except WebDriverException as wde:
            print(wde)

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
            for inp in inputs:
                if inp.get_attribute('type') == 'file':
                    inp.send_keys(avatar)
                    sleep(1)
                    return 
        except WebDriverException as ex:
            print('WDE EX AVATAR: ', ex)

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
            if not self._wait_until_homepage_load():
                return False
            self._decline_saving_login_data()
            return True
        except (WebDriverException, TimeoutException) as wte:
            return False

    def make_post(self, text=None, filename=None) -> bool:
        try:
            self._open_from_navbar('Create')
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            inputs[1].send_keys(IMG_DIR + 'instagram/' + filename)
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
        print(name, username, bio, gender, avatar)
        input_fields = {
            'pepName': name,
            'pepUsername': username,
            'pepBio': bio
        }
        if not self._edit_profile():
            return False
        try:
            for key, value in input_fields.items():
                if not value or value == 'None' or 'jpg' in value or 'png' in value:
                    continue
                field = self.wait(3).until(ec.presence_of_element_located((By.ID, key)))
                try:
                    field.clear()
                except Exception as ex:
                    pass
                field.send_keys(value)
            self._select_gender(gender)
            sleep(6)
            self._select_avatar(IMG_DIR + 'instagram/' + avatar)
            submit = self.driver.find_element(By.XPATH, '//div[contains(text(), "Submit")]')
            self.move_and_click(submit)
            sleep(3)
            self.open_homepage()
            return True
        except (TimeoutException, WebDriverException) as wde:
            pass
        return False

    def collect_feed(self, tag=None):
        if tag not in self.driver.current_url:
            self.driver.get(f'https://www.instagram.com/explore/tags/{tag}')
        sleep(5)
        self.scroll_to_the_end()
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
                self._save_new_post_to_db(*data)

        except StaleElementReferenceException as sere:
            pass

    def handle_posts(self, tag: str, posts_count: int):
        """
        author_name, text, img_path, posts_link, date, likes_amount, likes_accounts,
                             comments_amount, comments_accounts, retweets_amount, text_names, noun_keywords,
                             label, sent_rate, lang, tag
            'link': f'https://www.instagram.com' + i.get('href'),
            'text': i.find('img').get('alt'),
            'likes': likes,
            'comments': comments,
            'shares': None
        """
        posts = self.collect_posts(tag, posts_count)
        for post in posts:
            try:
                comments, likes = self._liked_and_commented_users(post['link']).values()
                rate = return_data_flair(post['text'])
                data = ['None', post['text'], 'None', post['link'], 'None', len(likes), likes, len(comments), comments,
                        'None', *rate[1:], tag]
                print('INSTAGRAM DATA: ', data)
                print()
                self._save_new_post_to_db(*data)
            except Exception as ex:
                print(ex)

    def collect_posts(self, tag, posts_count):
        retries = 0
        posts = []
        url = f'https://www.instagram.com/explore/tags/{tag}/'
        self.driver.get(url)
        try:
            self.wait(3).until(ec.presence_of_all_elements_located((By.XPATH, "//main[@role='main']//article//a")))
            link_arr = []
            posts = []
            while True:
                html = BeautifulSoup(self.driver.page_source, 'html.parser')
                content = html.find_all(
                    'main', {'role': "main"})[0].find('article')

                if "may be broken" in content.get_text():
                    return []
                posts_link = content.find_all('a')
                for n, i in enumerate(posts_link):
                    if i is None or i in link_arr:
                        break
                    elem = self.driver.find_elements(By.XPATH, '//main[@role="main"]//article//a')[n]
                    self.driver.execute_script("arguments[0].scrollIntoView();", elem)
                    self.move_and_click(elem, to_click=False)
                    try:
                        articles_inner = self.driver.find_elements(By.XPATH, '//main[@role="main"]//article//a')[n]
                        articles_inner = articles_inner.get_attribute('innerHTML')
                        articles_soup = BeautifulSoup(articles_inner, 'html.parser').find('div', {
                            'style': 'background: rgba(0, 0, 0, 0.3);'
                        })
                        likes, comments = [
                            int(e.get_text().replace('K', "00").replace('.', ",").replace(',', ""))
                            for e in articles_soup.find_all('li')
                            # for e in BeautifulSoup(self.driver.find_elements(By.XPATH,
                            #                                             '//main[@role="main"]//article//a')[n].get_attribute('innerHTML'),
                            #                        "html.parser").find('div', {
                            #     'style': 'background: rgba(0, 0, 0, 0.3);'}).find_all('li')
                        ]
                    except Exception:
                        likes = 0
                        comments = 0
                    id_ = str(time.time()).replace('.', '')[8:]
                    posts.append(
                        {'link': f'https://www.instagram.com' + i.get('href'),
                         'text': i.find('img').get('alt'),
                         'likes': likes,
                         'comments': comments,
                         'shares': None
                         })
                    link_arr.append(i.get('href'))
                length_posts = len(link_arr)

                if length_posts >= posts_count:
                    break
                if length_posts == 0:
                    retries += 1
                if retries == 3:
                    break

            if length_posts >= posts_count:
                posts = posts[0:posts_count - 1]
        except TimeoutException as e:
            pass
        return posts


if __name__ == '__main__':
    pass
