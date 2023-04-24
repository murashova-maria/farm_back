# LOCAL
from api import *


@app.get('/posts/')
async def get_feed(params: Dict[Any, Any]):
    data = {}
    try:
        posts = FeedDB.filter_posts(**params)
        for feed in posts:
            data.update({feed['post_id']: {}})
            for key, value in feed.items():
                data[feed['post_id']].update({key: value})
        return data
    except Exception as ex:
        print('EXCEPTION: ', ex)
        raise HTTPException(status_code=400, detail='Invalid data')
