# LOCAL
from api import *

# OTHER
import traceback


@app.post('/bots/{user_id}/schedules/')
async def bots_schedule(user_id: str, params: Dict[Any, Any]):
    try:
        post_data = None
        action = params.get('action')
        day = params.get('day')
        time_range = params.get('time_range')
        exact_time = datetime.now()
        if day is not None and time_range is not None:
            exact_time = get_randomized_date(int(day), RANGES[int(time_range)])
        # data = [user_id, action, day, time_range, exact_time]
        data = {
            'user_id': user_id,
            'action': action,
            'day': day,
            'time_range': time_range,
            'exact_time': exact_time
        }
        social_media = UserDB.filter_users(user_id=user_id)[0]['social_media']
        filename = None
        if action == 'make_post' and params:
            post_exist = SelfPostsDB.filter_posts(user_id=user_id, day=int(day),
                                                  time_range=int(time_range))
            if post_exist:
                main_queue.put(QueuedTask(SelfPostsDB, 'delete_post', {'post_id': post_exist[0]['post_id']}))
            image_base64 = params.get('filename')
            if params.get('filename') is not None:
                extension, image_base64 = image_base64.split(',')
                image_data = base64.b64decode(image_base64)
                if 'jpg' in extension or 'jpeg' in extension:
                    filename = f'{user_id}_post_image_{randint(0, 10000)}.jpg'
                else:
                    filename = f'{user_id}_post_image_{randint(0, 10000)}.png'
                # Save the binary data to a file using asyncio and aiofiles
                async with aiofiles.open(IMG_DIR + f'{social_media}/' + filename, 'wb') as f:
                    await f.write(image_data)
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
        # data += ['None', params.get('scroll_minutes')]
        data.update({'status': 'None', 'scroll_minutes': params.get('scroll_minutes')})
        main_queue.put(QueuedTask(ScheduleDB, 'create_schedule', data))
        final_data = {'day': day, 'time_range': time_range, 'action': action}
        if post_data is not None:
            final_data.update({**post_data})
        return final_data
    except Exception as ex:
        traceback.print_exc()
        print(ex)
        raise HTTPException(status_code=400, detail=[])


@app.post('/bots/{user_id}/self_posts/')
async def create_self_post(user_id, params: Dict[Any, Any]):
    try:
        day = params.get('day')
        time_range = params.get('time_range')
        image = params.get('filename')
        if image:
            extension, image = image.split(',')
        social_media = UserDB.filter_users(user_id=user_id)[0]['social_media']
        filename = f'{user_id}_post_image_{randint(0, 10000)}.jpg'
        if image:
            image = base64.b64decode(image)
            with open(IMG_DIR + f'{social_media}/' + filename, 'wb') as output:
                output.write(image)
        post_data = {
            'user_id': user_id,
            'text': params.get('text'),
            'filename': filename,
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


@app.get('/bots/schedules/{user_id}/')
async def get_schedules_by_params(user_id: str, day: int = None, time_range: int = None):
    try:
        params = {'user_id': user_id}
        if day is not None:
            params.update({'day': day})
        if time_range is not None:
            params.update({'time_range': time_range})
        schedules = ScheduleDB.filter_schedules(**params)
        data = []
        for schedule in schedules:
            if schedule['action'] == 'None' or schedule['action'] is None:
                main_queue.put(QueuedTask(ScheduleDB, 'delete_schedule', {'schedule_id': schedule['schedule_id']}))
                continue
            tmp_data = {}
            if schedule['action'] == 'make_post':
                tmp_params = {}
                if time_range is not None:
                    tmp_params.update({'time_range': time_range})
                if day is not None:
                    tmp_params.update({'day': day})
                publication = SelfPostsDB.filter_posts(user_id=schedule['user_id'], **tmp_params)
                if publication:
                    publication = publication[0]
                    tmp_data.update({'publication_text': publication['text']})
                    if publication['filename'] and publication['filename'] != 'None':
                        tmp_data.update({'filename': True})
            tmp_data.update({key: value for key, value in schedule.items()})
            data.append(tmp_data)
        return data
    except Exception as ex:
        print(ex)
        traceback.print_exc()


@app.delete('/bots/schedules/{user_id}/delete/')
async def delete_schedule_range(user_id: str, day: int = None, time_range: int = None):
    try:
        get_schedules = ScheduleDB.filter_schedules(user_id=user_id, day=day, time_range=time_range)
        if not get_schedules:
            return {'INFO': "Schedule doesn't exist."}
        get_schedules = get_schedules[0]
        if get_schedules['action'] == 'make_post':
            get_post = SelfPostsDB.filter_posts(user_id=user_id, day=day, time_range=time_range)
            if get_post:
                main_queue.put(QueuedTask(SelfPostsDB, 'delete_post', {'post_id': get_post['post_id']}))
        main_queue.put(QueuedTask(ScheduleDB, 'delete_schedule', {'schedule_id': get_schedules['schedule_id']}))
        return {'STATUS': "OK"}
    except Exception as ex:
        raise HTTPException(status_code=400, detail='WRONG DATA')
