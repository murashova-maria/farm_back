# LOCAL
from api import *


@app.post('/bots/{user_id}/schedules/')
async def bots_schedule(user_id: str, params: Dict[Any, Any]):
    try:
        action = params.get('action')
        day = params.get('day')
        time_range = params.get('time_range')
        exact_time = get_randomized_date(int(day), RANGES[int(time_range)])
        data = [user_id, action, day, time_range, exact_time]
        if action == 'make_post' and params:
            post_data = {
                'user_id': user_id,
                'text': params.get('text'),
                'filename': params.get('filename'),
                'status': 'None',
                'day': day,
                'time_range': time_range,
                'exact_time': exact_time,
            }
            main_queue.put(QueuedTask(SelfPostsDB, 'create_post', post_data))
        main_queue.put(QueuedTask(ScheduleDB, 'create_schedule', data))
        return {'Status': "OK"}
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail=[])


@app.post('/bots/{user_id}/self_posts/')
async def create_self_post(user_id, params: Dict[Any, Any]):
    try:
        day = params.get('day')
        time_range = params.get('time_range')
        post_data = {
            'user_id': user_id,
            'text': params.get('text'),
            'filename': params.get('filename'),
            'status': 'None',
            'day': day,
            'time_range': time_range,
            'exact_time': get_randomized_date(int(day), RANGES[int(time_range)])

        }
        main_queue.put(QueuedTask(SelfPostsDB, 'create_post', post_data))
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail=[])


@app.get('/bots/{user_id}/schedules/')
async def bots_schedule(user_id: str):
    try:
        schedules = ScheduleDB.filter_schedules(user_id=user_id)
        full_schedule = [["" for _ in range(11)] for _ in range(7)]
        for schedule in schedules:
            try:
                day = schedule['day']
                time_range = schedule['time_range']
                full_schedule[int(day)][int(time_range)] = schedule['action']
            except Exception as ex:
                pass
        return full_schedule
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail=[])
