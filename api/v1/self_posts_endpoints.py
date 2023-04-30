# LOCAL
from api import *


@app.get('/accounts/{user_id}/self_posts/')
async def get_self_posts(user_id: str):
    data = []
    posts = SelfPostsDB.filter_posts(user_id=user_id)
    if not posts:
        raise HTTPException(status_code=400, detail='User does not have posts')
    for post in posts:
        ld = {}
        for key, value in post.items():
            ld.update({key: value})
        data.append(ld)
    return data


@app.post('/accounts/{user_id}/self_posts/')
async def add_self_post(user_id: str, items: Dict[Any, Any]):
    try:
        text = items.get('text')
        filename = items.get('filename')
        # filename = f'{user_id}_post_image_{randint(0, 10000)}.jpg'
        exact_time = items.get('exact_time')
        task = QueuedTask(SelfPostsDB, 'create_post', [user_id, text, filename, 'None', 'None', 'None',
                                                       exact_time])
        main_queue.put(task)
        return {'Status': 'Success'}
    except Exception as ex:
        print('EX: ', ex)
        raise HTTPException(status_code=404, detail='Wrong data was sent')
