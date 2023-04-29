# LOCAL
from api import *


@app.get('/posts/')
async def get_feed(social_media: Optional[str] = None, country: Optional[str] = None):
    data: List[Dict[str, Any]] = []
    try:
        if social_media and country:
            posts = FeedDB.filter_posts(social_media=social_media, country=country)
        elif social_media:
            posts = FeedDB.filter_posts(social_media=social_media)
        elif country:
            posts = FeedDB.filter_posts(country=country)
        else:
            posts = FeedDB.get_all()

        for feed in posts:
            ld = {}
            for key, value in feed.items():
                ld.update({key: value})
            ld.update({'username': 'None'})
            data.append(ld)
        return data
    except Exception as ex:
        print('EXCEPTION: ', ex)
        raise HTTPException(status_code=400, detail='Invalid data')
