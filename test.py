# OTHER
from time import sleep

# LOCAL
from loader import *


if __name__ == '__main__':
    # main_queue.put(QueuedTask(UserDB, 'create_user', {'username': '+33783473178', 'password': 'cBtue9fa5uTtZpx',
    #                                                   'social_media': 'twitter', 'phone_number': '+33783473178',
    #                                                   'status': 'active', 'activity': 'wait',
    #                                                   'reg_date': datetime.datetime.now().timestamp()}))
    # task = main_queue.get()
    # task()
    # main_queue.task_done()
    args = {'username': '+33783473178'}
    print([usr.username for usr in UserDB.filter_users(**args)])
    # for user in session.query(TwitterProfileBase).all():
    #     # session.delete(user)
    #     # session.commit()
    #     print(user.__dict__)
