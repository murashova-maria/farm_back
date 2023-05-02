# LOCAL
from api import *


@app.post('/bots/{user_id}/schedules/')
async def bots_schedule(user_id: str, params: Dict[Any, Any]):
    try:
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
