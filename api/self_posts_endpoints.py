# LOCAL
from api import *


@app.get('/accounts/{user_id}/self_posts/')
async def get_self_posts(user_id: str):
    data = {}
    posts = SelfPostsDB.filter_posts(user_id=user_id)
    if not posts:
        raise HTTPException(status_code=400, detail='User does not have posts')
    for post in posts:
        data.update({user_id: {}})
        for key, value in post.items():
            data[user_id].update({key: value})
    return data


@app.post('/accounts/{user_id}/self_posts/')
async def add_self_post(user_id: str, items: Dict[Any, Any]):
    print('USER ID:', user_id)
    try:
        print(user_id)
        social_media = items.get('social_media')
        text = items.get('text')
        filename = items.get('filename')
        status = items.get('status')
        task = QueuedTask(SelfPostsDB, 'create_post', [user_id, social_media, text, filename,
                                                       status, datetime.now().strftime(DATE_FORMAT)])
        main_queue.put(task)
        return {'Status': 'Success'}
    except Exception as ex:
        print('EX: ', ex)
        raise HTTPException(status_code=404, detail='Wrong data was sent')
