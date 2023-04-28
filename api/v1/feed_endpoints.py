# LOCAL
from api import *


@app.get('/posts/')
async def get_feed(params: Optional[Dict[Any, Any]] = None):
    data = []
    try:
        if params:
            posts = FeedDB.filter_posts(**params)
        else:
            posts = FeedDB.get_all()
        for feed in posts:
            ld = {}
            for key, value in feed.items():
                ld.update({key: value})
            data.append(ld)
        return data
    except Exception as ex:
        print('EXCEPTION: ', ex)
        raise HTTPException(status_code=400, detail='Invalid data')
