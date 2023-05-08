# LOCAL
from loader import *
from api.v1.endpoints import *
from api.v2.endpoints import *
from api.utils import ready_to_post

# THREADING
import threading

# OTHER
from time import sleep
from pyvirtualdisplay import Display


# display = Display(visible=False, size=(1920, 1080))
# display.start()


def make_post():
    while True:
        sleep(2)
        for post in SelfPostsDB.filter_posts(status=None):
            try:
                if ready_to_post(post['exact_time']):
                    main_queue.put(QueuedTask(SelfPostsDB, 'update_post', {'status': 'do_post',
                                                                           'post_id': post['post_id']}))
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'activity': 'make_post', 'status': 'gardering',
                                                                      'user_id': post['user_id']}))
            except (ValueError, TypeError) as te:
                print('MAKE_POST: ', te)


def check_schedule():
    while True:
        sleep(4)
        try:
            for schedule in ScheduleDB.filter_schedules(status=None):
                # print(schedule)
                if ready_to_post(schedule['exact_time']):
                    main_queue.put(QueuedTask(ScheduleDB, 'update_schedule', {
                        # 'day': schedule['day'],
                        # 'time_range': schedule['time_range'],
                        # 'user_id': schedule['user_id'],
                        'status': 'done',
                        'action': schedule['action'],
                        'schedule_id': schedule['schedule_id'],
                        # 'exact_time': schedule['exact_time']
                    }))
                    main_queue.put(QueuedTask(UserDB, 'update_user', {'activity': schedule['action'],
                                                                      'status': 'gardering',
                                                                      'user_id': schedule['user_id']}))
        except (ValueError, TypeError) as te:
            print('CHECK_SCHEDULE: ', te)


def handle_queue():
    while True:
        sleep(0.1)
        task = main_queue.get()
        task()
        main_queue.task_done()


t1 = threading.Thread(target=handle_queue)
t1.daemon = True
t1.start()
t2 = threading.Thread(target=make_post)
t2.daemon = True
t2.start()
t3 = threading.Thread(target=check_schedule)
t3.daemon = True
t3.start()


if __name__ == '__main__':
    # local_graph.delete_all()
    pass
