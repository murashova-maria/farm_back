# OTHER
from time import sleep

# LOCAL
from loader import *


if __name__ == '__main__':
    # local_graph.delete_all()
    # usr_id = "7f7adb23-bf27-4bb3-a2c6-cc71a6d17a43"
    sh = ScheduleDB
    for schedule in sh.get_all_schedules():
        print(schedule)
        # local_graph.delete(schedule)
    # kw.add_keyword_to_user('New dog', usr_id, 15)
    # print(kw.get_all_keywords_with_users())
    # print(kw.get_keywords_by_user_id(usr_id, only_kw=True))
    # for post in SelfPostsDB.filter_posts(user_id=usr_id):
    #     local_graph.delete(post)
    # for schedule in ScheduleDB.filter_schedules(user_id=usr_id):
    #     local_graph.delete(schedule)
    pass
