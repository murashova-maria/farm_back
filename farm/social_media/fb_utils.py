try:
    from .base import *
except ImportError:
    from base import *
from dateutil import parser
from bs4 import BeautifulSoup


def content_parsing(content2):
    account = content2.find_all('a', {'role': 'link', 'tabindex': '0'})[1].get(
        'href').replace('https://www.facebook.com/', '')
    account = 'https://www.facebook.com/' + account
    account_name = content2.find_all('a', {'role': 'link', 'tabindex': '0'})[1].get_text()
    try:
        post_text = content2.find(
            'div', {'data-ad-comet-preview': 'message'}).text
    except Exception as e:
        post_text = ''
    if post_text == '':
        try:
            post_text = content2.find('blockquote').text.replace(
                'See original', '').replace('Rate this translation', '').replace('·', '').replace('See more',
                                                                                                  '').strip()
        except Exception as e:
            post_text = ''
    if post_text == "Facebook":
        try:

            post_text = "\n".join([el_text.get_text() for el_text in content2.find_all('div',{'style':'text-align: start;'})])
        except Exception:
            pass
    post_text.replace("See more","")
    try:
        date = content2.find_all('a', {'role', 'link'})[2]
        date = date.find('span').text
        if 'Yesterday' in date:
            date = datetime.datetime.now().date()
        else:
            date = parser.parse(date)

    except Exception as e:
        date = datetime.datetime.now().date()
    link = "no link"
    id_ = str(time.time()).replace('.', '')[8:]
    try:
        likes = int(
            content2.find('div', {'aria-label': re.compile('Like:')}).get('aria-label').replace('Like:', '').replace(
                'people', '').replace(' ', '').replace('K', "00").replace('.', ",").replace(',', "").replace('Like', ''))
        print("Likes",likes)
    except Exception as e:
        print(e)
        likes = 0

    try:
        comments = int(
            [el for el in content2.find_all('div', {'role': 'button'}) if el.find('span', {
                'dir': 'auto'})][0].find('span', {
                'dir': 'auto'}).get_text().replace('comments', '').replace('comment', '').replace(' ', '').replace('K', "00").replace('.',",").replace(
                ',', ""))
        print("comments",comments)
    except Exception as e:
        print(e)
        comments = 0
        # shares
    try:
        shares = ([el.find('span', {'dir': 'auto'}) for el in content2.find_all('div', {'role': 'button'}) if
                   el.find('span', {'dir': 'auto'})])
        for el in shares:
            if 'share' in el.get_text():
                shares = int(el.get_text().replace('shares', '').replace('share', '').replace(' ', '').replace('K',
                                                                                                               "00").replace(
                    '.', ",").replace(',', ""))
                print("shares", shares)
                break
        if type(shares) != int:
            shares = 0
        print(shares)
    except Exception as e:
        print(e)
        shares = 0

    data = {'text': post_text, 'account': account_name, 'account_link': account,
            'date': date, 'link': link, 'id': id_, 'likes': likes, 'comments': comments,
            'shares': shares}
    return data


def check_exists_by_xpath(browser, xpath):
    try:
        el = browser.find_element(By.XPATH,
                                  xpath)
    except Exception:
        return False
    return True


def els_m(browser, xpath):
    try:
        els = browser.find_elements(By.XPATH,
                                    xpath)
    except Exception:
        return 0
    return len(els)


def parsing_posts(tag, posts_count, driver, recent=True):
    """Parsing posts"""
    result = []
    people_a = []
    if driver:
        articles = []
        try:
            url = f'https://www.facebook.com/search/posts?q={tag}"'
            if recent:
                url += '&filters=eyJyZWNlbnRfcG9zdHM6MCI6IntcIm5hbWVcIjpcInJlY2VudF9wb3N0c1wiLFwiYXJnc1wiOlwiXCJ9In0%3D'
            driver.get(url)
            time.sleep(2)
            WebDriverWait(driver, 30).until(
                ec.presence_of_all_elements_located((By.XPATH, "//div[@role='feed']//a[@role='link' and @tabindex='0']")))
            time.sleep(3)
            articles = driver.find_elements(
                By.XPATH, "//div[@role='feed']/div")
        except Exception as e:
            pass

        num = 0
        links = []
        pics = []
        dates = []
        while num < posts_count:
            try:
                post = driver.find_element(By.XPATH, "//div[@role='feed']/div[" + str(
                                              num + 1) + "]")
            except Exception:
                break
            driver.execute_script("arguments[0].scrollIntoView()", post)
            try:
                pic = driver.find_element(By.XPATH,
                                          "//div[@role='feed']/div[" + str(
                                              num + 1) + "]")
                pic = BeautifulSoup(pic.get_attribute("innerHTML"),
                                    "html.parser").find('image')['xlink:href']

            except Exception as e:
                print(e)
                pic = 'no pic'
            print(pic)
            pics.append(pic)
            try:
                date_el = driver.find_element(By.XPATH,
                                              "//div[@role='feed']/div[" + str(
                                                  num + 1) + "]//span/span[2 or 3]/span//a/span/../..")
                date_el_text = driver.find_element(By.XPATH,
                                                   "//div[@role='feed']/div[" + str(
                                                       num + 1) + "]//span[2 or 3]/span//a/span/../../..")
            except Exception as e:
                print('no date')
            driver.execute_script("window.scrollBy(0,-150)")
            time.sleep(5)
            print('scroll')
            try:
                actions = ActionChains(driver)
                actions.move_to_element(date_el).perform()
                time.sleep(3)
                link = BeautifulSoup(date_el.get_attribute("innerHTML"),
                                     "html.parser")
                link = link.find('a')['href']
                id_date = (BeautifulSoup(date_el_text.get_attribute("innerHTML"),
                                         "html.parser").find('span').get('aria-describedby'))
                date_text = (BeautifulSoup(driver.find_element(By.ID, id_date).get_attribute("innerHTML"),
                                           "html.parser").get_text())
                print(link)
                links.append(link)
                dates.append(date_text)

            except Exception as e:
                links.append('no link')
                dates.append('no date')
                link = "no link"

            num += 1
            time.sleep(3)

            actions = ActionChains(driver)
            actions.move_to_element(post).perform()
            time.sleep(2)
            content2 = BeautifulSoup(post.get_attribute('innerHTML'), 'html.parser')
            try:
                likes_count = int(
                    content2.find('div', {'aria-label': re.compile('Like:')}).get('aria-label').replace('Like:',
                                                                                                        '').replace(
                        'people', '').replace(' ', '').replace('K', "00").replace('.', ",").replace(',', "").replace(
                        'Like', ''))
                print("Likes", likes_count)
            except Exception as e:
                print(e)
                likes_count = 0

            if check_exists_by_xpath(driver, "//img[@role='presentation']") and likes_count>10:
                # pass
                for i in driver.find_elements(By.XPATH,
                                              "//div[@role='feed']/div[" + str(
                                                  num) + "]//img[@role='presentation']"):
                    driver.execute_script("arguments[0].click()", i)
                    time.sleep(6)
                    last_n = 0
                    start_sec = datetime.datetime.now()
                    while check_exists_by_xpath(driver,
                                                "//div[@role='dialog']//div[@role='progressbar']"):
                        if (datetime.datetime.now() - start_sec).seconds >= 3:
                            time.sleep(2)
                            start_sec = datetime.datetime.now()
                            if last_n == els_m(driver,
                                               "//div[@role='dialog']/div/div/div/div/div/div/div/div//div[@data-visualcompletion='ignore-dynamic']") or last_n > 1000:
                                # close_btn = driver.find_element(By.XPATH,
                                #                                 "//div[@aria-label='Close' or @aria-label='Закрыть']")
                                # driver.execute_script("arguments[0].click();", close_btn)
                                time.sleep(2)
                                break
                            last_n = els_m(driver,
                                           "//div[@role='dialog']/div/div/div/div/div/div/div/div//div[@data-visualcompletion='ignore-dynamic']")
                        try:
                            l = driver.find_element(By.XPATH, "//div[@role='dialog']//div[@role='progressbar']")
                            driver.execute_script("arguments[0].scrollIntoView()", l)
                        except Exception:
                            pass
                        time.sleep(0.6)
                    people = driver.find_elements(By.XPATH,
                                                  "//div[@role='dialog']/div/div/div/div/div/div/div/div//div[@data-visualcompletion='ignore-dynamic']")
                    people = [BeautifulSoup(p.get_attribute('innerHTML'), 'html.parser') for p in people]
                    for l in people:
                        try:
                            name = l.find('a').get('aria-label')
                            link_n = l.find('a').get('href')
                            people_a.append(
                                {'tag': tag, "tag_id": tag, 'name': name, 'facebook_link': link_n, "twitter_link": None,"instagram_link": None,
                                 'post': link, 'like': True, 'share': False,'network':"Facebook",
                                 'comment': False})
                        except Exception as e:
                            pass
                    try:
                        close_btn = driver.find_element(By.XPATH, "//div[@aria-label='Close' or @aria-label='Закрыть']")
                        driver.execute_script("arguments[0].click();", close_btn)
                        time.sleep(4)
                    except Exception as e:
                        pass
                    try:
                        close_btn = driver.find_element(By.XPATH, "//div[@aria-label='Close' or @aria-label='Закрыть']")
                        driver.execute_script("arguments[0].click();", close_btn)
                        time.sleep(4)
                    except Exception as e:
                        pass
                try:
                    comments = driver.find_elements(By.XPATH,
                                                    "//div[@role='feed']/div[" + str(
                                                        num) + "]//div[@role='button']/span[@dir='auto']")[0]
                    driver.execute_script("arguments[0].click()", comments)
                    time.sleep(6)
                except Exception:
                    pass
                last_n = 0
                start_sec = datetime.datetime.now()
                comments = []
                try:
                    comments = \
                        driver.find_elements(By.XPATH,
                                             "//ul/li//div[contains(@aria-label,'Comment by')]")
                    # people = comments.find_elements(By.XPATH,
                    #                                   "//div[@role='dialog']/div/div/div/div/div/div//h3/span/a[@role='link']")
                    comments = [BeautifulSoup(c.get_attribute('innerHTML'), 'html.parser')
                                for c in comments if
                                BeautifulSoup(c.get_attribute('innerHTML'), 'html.parser').find('a', {
                                    'role': 'link', 'aria-hidden': 'false'})]
                except Exception:
                    pass
                try:
                    most_rel = driver.find_element(By.XPATH,"//span[contains(text(),'Most relevant')]")
                    driver.execute_script("arguments[0].click()", most_rel)
                    time.sleep(2)
                    most_rel = driver.find_element(By.XPATH,"//span[contains(text(),'All comments')]")
                    driver.execute_script("arguments[0].click()", most_rel)
                    time.sleep(2)

                except Exception:
                    pass
                for c in comments:
                    # print(c)
                    try:
                        name = c.find('a', {'role': 'link','aria-hidden': 'false'}).get_text()
                        # print(name)
                        link_n = c.find('a', {'role': 'link','aria-hidden': 'false'}).get('href')
                        comment_text = c.find_all('span',{'dir':'auto'})[1].get_text()
                        # print(link_n)
                        # print(link)
                        people_a.append(
                            {'tag': tag, 'name': name, 'facebook_link': link_n, 'post': link, 'like': False, 'share': False,"text":comment_text,
                             'comment': True})
                        print({'tag': tag, 'name': name, 'facebook_link': link_n, 'post': link, 'like': False, 'share': False,"text":comment_text,
                             'comment': True})
                        # print('__________________________________________________________')
                    except Exception:
                        pass
                try:
                    close_btn = driver.find_element(By.XPATH, "//div[@aria-label='Close' or @aria-label='Закрыть']")
                    driver.execute_script("arguments[0].click();", close_btn)
                    time.sleep(2)
                except Exception as e:
                    pass
                print(len(people_a))
                try:
                    shares = driver.find_elements(By.XPATH,
                                                  "//div[@role='feed']/div[" + str(
                                                      num) + "]//div[@role='button']/span[@dir='auto']")[1]
                    driver.execute_script("arguments[0].scrollIntoView()", shares)
                    driver.execute_script("window.scrollBy(0,-150)")
                    time.sleep(1)
                    driver.execute_script("arguments[0].click()", shares)
                except Exception:
                    pass
                last_n = 0
                start_sec = datetime.datetime.now()
                while check_exists_by_xpath(driver,
                                            "//div[@role='dialog']//div[@role='progressbar']"):
                    if (datetime.datetime.now() - start_sec).seconds >= 3:
                        time.sleep(2)
                        start_sec = datetime.datetime.now()
                        if last_n == els_m(driver,
                                           "//div[@role='dialog']/div/div/div/div/div/div/div/div//div["
                                           "@data-visualcompletion='ignore-dynamic']") or last_n > 1000:
                            time.sleep(2)
                            break
                        last_n = els_m(driver,
                                       "//div[@role='dialog']/div/div/div/div/div/div/div/div//div["
                                       "@data-visualcompletion='ignore-dynamic']")
                        print(last_n)
                    try:
                        l = driver.find_element(By.XPATH, "//div[@role='dialog']//div[@role='progressbar']")
                        driver.execute_script("arguments[0].scrollIntoView()", l)
                    except Exception:
                        pass
                    time.sleep(0.6)
                    people = driver.find_elements(By.XPATH,
                                                  "//div[@role='dialog']//h3/span/a[@role='link']/..")
                    people = [BeautifulSoup(p.get_attribute('innerHTML'), 'html.parser') for p in people]
                    for l in people:
                        try:
                            name = l.find('a').get_text()
                            link_n = l.find('a').get('href')
                            people_a.append(
                                {'tag': tag, 'name': name, 'facebook_link': link_n, "twitter_link": None,"instagram_link": None, 'post': link, 'like': False,
                                 'share': True,
                                 'comment': False,'network':"Facebook",})
                        except Exception as e:
                            pass
                try:
                    close_btn = driver.find_element(By.XPATH, "//div[@aria-label='Close' or @aria-label='Закрыть']")
                    driver.execute_script("arguments[0].click();", close_btn)
                    time.sleep(2)
                except Exception as e:
                    pass
                print(len(people_a))

            articles = driver.find_elements(
                By.XPATH, "//div[@role='feed']/div")

            length_posts = len(articles[1:])
        if length_posts > posts_count:
            articles = articles[0:posts_count]
            dates = dates[0:posts_count]
            links = links[0:posts_count]
            pics = pics[0:posts_count]
            length_posts = posts_count
        print(links)
        print(f'[FACEBOOK]: Post count: {length_posts}')
        article_arr = [BeautifulSoup(e.get_attribute('innerHTML'), 'html.parser') for e in articles[0:]
                       if len(BeautifulSoup(e.get_attribute('innerHTML'), 'html.parser').find_all('a', {'role': 'link', 'tabindex': '0'}))>2]
        with open('page.html', 'w', encoding="utf-8") as f:
            f.write(driver.page_source)
        for num, i in enumerate(article_arr):
            print(links[num])
            print(dates[num])
            if "/ads/" not in links[num] and dates[num] != 'no date' and links[
                num] != 'no link' :
                data = content_parsing(i)
                if data['text'].strip() != "" and data['text'] != "Facebook":
                    print(data['text'])

                    data['tag'] = tag
                    data['tag_id'] = tag
                    data['network'] = 'facebook'
                    data['link'] = links[num]
                    try:
                        dates[num] = dates[num].split(",")
                        dates[num] = dates[num][1].strip() + dates[num][2].replace("at", "")
                        dates[num] = (datetime.strptime(dates[num], "%B %d %Y %H:%M %p"))
                    except Exception as e:
                        continue
                    data['date'] = dates[num]
                    data['date'] = dates[num]
                    data['pic'] = pics[num]
                    result.append(data)
            time.sleep(4)
    else:
        print('Login error')
    return result, people_a