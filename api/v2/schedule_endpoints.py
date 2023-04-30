# LOCAL
from api import *

# OTHER
import aiofiles


@app.post('/bots/{user_id}/schedules/')
async def bots_schedule(user_id: str, params: Dict[Any, Any]):
    try:
        action = params.get('action')
        day = params.get('day')
        time_range = params.get('time_range')
        exact_time = get_randomized_date(int(day), RANGES[int(time_range)])
        data = [user_id, action, day, time_range, exact_time]
        social_media = UserDB.filter_users(user_id=user_id)[0]['social_media']
        if action == 'make_post' and params:
            filename = f'{user_id}.jpg'
            if params.get('filename') is not None:
                async with aiofiles.open(IMG_DIR + f'{social_media}/' + filename, 'wb') as f:
                    await f.write(params.get('filename').read())
            post_data = {
                'user_id': user_id,
                'text': params.get('text'),
                'filename': filename,
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
