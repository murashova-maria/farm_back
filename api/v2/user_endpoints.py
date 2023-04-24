# LOCAL
from api import *


def start(username, password, phone_number, network, proxy=None):
    net = Starter(username, password, phone_number, network, proxy)
    if net.network == 'facebook':
        net.start_facebook()
    elif net.network == 'twitter':
        net.start_twitter()
    elif net.network == 'instagram':
        net.start_instagram()


@app.get('/bots/')
async def get_bots_info(social_media: str = None, country: str = None):
    try:
        params = {}
        if social_media:
            params.update({'social_media': social_media})
        if country:
            params.update({'country': country})
        if params:
            return [{key: value for key, value in user.items()} for user in UserDB.filter_users(**params)]
        else:
            return [{key: value for key, value in user.items()} for user in UserDB.get_all()]
    except Exception as ex:
        raise HTTPException(status_code=400, detail=[])


@app.get('/bots/{user_id}/keywords/')
async def keywords_by_usrid(user_id: str):
    try:
        return KeywordDB.get_keywords_by_user_id(user_id)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=[])
