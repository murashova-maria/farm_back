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
        if day and time_range:
            exact_time = get_randomized_date(int(day), RANGES[int(time_range)])
        data = [user_id, action, day, time_range, exact_time]
        social_media = UserDB.filter_users(user_id=user_id)[0]['social_media']
        filename = f'{user_id}_post_image_{randint(0, 10000)}.jpg'
        if action == 'make_post' and params:
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
        data += ['None', params.get('scroll_minutes')]
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


@app.get('/bots/schedules/')
async def get_schedules_by_params(day: int = None, time_range: int = None):
    try:
        params = {}
        if day:
            params.update({'day': day})
        if time_range:
            params.update({'time_range': time_range})
        schedules = ScheduleDB.filter_schedules(**params)
        data = []
        for schedule in schedules:
            tmp_data = {}
            if schedule['action'] == 'make_post':
                tmp_params = {}
                if time_range:
                    tmp_params.update({'time_range': time_range})
                if day:
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
