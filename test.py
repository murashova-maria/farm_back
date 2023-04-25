# OTHER
from time import sleep

# LOCAL
from loader import *
from farm.social_media.instagram import Instagram


if __name__ == '__main__':
    usr_id = "742f3cd1-503a-4ee3-bb62-0699a9262760"
    ScheduleDB.create_schedule(usr_id, 'New Action', 5, 5)
    # for i in ScheduleDB.filter_schedules(user_id=usr_id):
    #     local_graph.delete(i)
    print(ScheduleDB.filter_schedules(user_id=usr_id))
