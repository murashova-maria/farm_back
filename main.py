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


print(os.getpid())
# display = Display(visible=False, size=(1920, 1080))
# display.start()


def make_post():
    while True:
        sleep(2)
        for post in SelfPostsDB.filter_posts(status='None'):
            if ready_to_post(post['date']):
                main_queue.put(QueuedTask(SelfPostsDB, 'update_post', {'status': 'do_post',
                                                                       'post_id': post['post_id']}))
                main_queue.put(QueuedTask(UserDB, 'update_user', {'activity': 'make_post', 'status': 'in process',
                                                                  'user_id': post['user_id']}))


def handle_queue():
    while True:
        sleep(0.5)
        task = main_queue.get()
        task()
        main_queue.task_done()


t1 = threading.Thread(target=handle_queue)
t1.daemon = True
t1.start()
t2 = threading.Thread(target=make_post)
t2.daemon = True
t2.start()


if __name__ == '__main__':
    # local_graph.delete_all()
    pass
