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
        return [{'keyword': key['keyword'], 'keyword_id': key['keyword_id']}
                for key in KeywordDB.get_keywords_by_user_id(user_id, only_kw=False)]
    except Exception as ex:
        raise HTTPException(status_code=400, detail=[])


@app.post('/bots/new/')
async def create_account(item: Dict[Any, Any]):
    username = item.get('username')
    password = item.get('password')
    phone_number = item.get('phone_number')
    network = item.get('network')
    proxy = item.get('proxy')
    if None in (username, password, phone_number, network):
        raise HTTPException(status_code=400, detail='Missing parameter(s)')
    if network not in ('twitter', 'facebook', 'instagram'):
        raise HTTPException(status_code=400, detail='Invalid network')
    thread = Thread(target=start, args=(username, password, phone_number, network, proxy))
    thread.start()
    return {'Success': 'User creation started'}
