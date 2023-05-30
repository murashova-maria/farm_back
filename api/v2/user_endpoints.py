# LOCAL
import traceback

from api import *


def start(username, password, phone_number, network, proxy=None, country='None', gologin_profile_id=None,
          auth_code=None):
    net = Starter(username, password, phone_number, network, proxy, country, gologin_profile_id, auth_code)
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
            users = [{key: value for key, value in user.items()} for user in UserDB.filter_users(**params)]
            for index, user in enumerate(users):
                amount_of_posts = len(SelfPostsDB.filter_posts(user_id=user['user_id']))
                if user['social_media'] == 'twitter':
                    prf = TwitterProfileDB.filter_profiles(user_id=user['user_id'])[0]
                    name = prf['name']
                    avatar = prf['avatar']
                elif user['social_media'] == 'facebook':
                    prf = FacebookProfileDB.filter_profiles(user_id=user['user_id'])[0]
                    name = prf['name']
                    avatar = prf['avatar']
                else:
                    prf = InstagramProfileDB.filter_profiles(user_id=user['user_id'])[0]
                    name = prf['name']
                    avatar = prf['avatar']
                users[index].update({'amount_of_posts': amount_of_posts})
                if name != 'None' and name is not None:
                    users[index].update({'username': name})
                if avatar is not None:
                    users[index].update({'avatar': True})
                else:
                    users[index].update({'avatar': False})
            return users
        else:
            users = [{key: value for key, value in user.items()} for user in UserDB.get_all()]
            print(users)
            for index, user in enumerate(users):
                # amount_of_posts = len(SelfPostsDB.filter_posts(user_id=user['user_id']))
                if user['social_media'] == 'twitter':
                    prf = TwitterProfileDB.filter_profiles(user_id=user['user_id'])[0]
                    name = prf['name']
                    avatar = prf['avatar']
                elif user['social_media'] == 'facebook':
                    prf = FacebookProfileDB.filter_profiles(user_id=user['user_id'])[0]
                    name = prf['name']
                    avatar = prf['avatar']
                else:
                    prf = InstagramProfileDB.filter_profiles(user_id=user['user_id'])[0]
                    name = prf['name']
                    avatar = prf['avatar']
                # users[index].update({'amount_of_posts': amount_of_posts})
                if name != 'None' and name is not None:
                    users[index].update({'username': name})
                if avatar is not None:
                    users[index].update({'avatar': True})
                else:
                    users[index].update({'avatar': False})
            return users
    except Exception as ex:
        traceback.print_exc()
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
    auth_code = item.get('auth_code')
    if not phone_number:
        phone_number = item.get('email')
    network = item.get('network')
    proxy = item.get('proxy')
    country = item.get('country')
    gologin_profile = item.get('gologin_profile_id')
    if None in (username, password, phone_number, network):
        raise HTTPException(status_code=400, detail='Missing parameter(s)')
    if network not in ('twitter', 'facebook', 'instagram'):
        raise HTTPException(status_code=400, detail='Invalid network')
    thread = Thread(target=start, args=(username, password, phone_number, network, proxy, country, gologin_profile,
                                        auth_code))
    thread.start()
    return {'Success': 'User creation started'}


@app.get('/bots/{user_id}/avatar/')
async def return_users_avatar(user_id: str):
    users_object = UserDB.filter_users(user_id=user_id)
    if not users_object or users_object is None:
        return {'Error': 'Wrong user_id'}
    sm = users_object[0]['social_media']
    if sm == 'facebook':
        profile = FacebookProfileDB.filter_profiles(user_id=user_id)[0]
    elif sm == 'twitter':
        profile = TwitterProfileDB.filter_profiles(user_id=user_id)[0]
    else:
        profile = InstagramProfileDB.filter_profiles(user_id=user_id)[0]
    file_path = f'{IMG_DIR}{sm}/{profile["avatar"]}'
    print(file_path)
    return FileResponse(file_path, media_type='application/octet-stream', filename=profile['avatar'])


@app.get('/attachment/')
async def get_files(user_id: str, day: int, time_range: int):
    try:
        users_object = UserDB.filter_users(user_id=user_id)
        if not users_object or users_object is None:
            return {'Error': 'Wrong user_id'}
        sm = users_object[0]['social_media']
        publication = SelfPostsDB.filter_posts(user_id=user_id, day=day, time_range=time_range)[0]
        file_path = f'{IMG_DIR}{sm}/{publication["filename"]}'
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_path)
    except Exception as ex:
        traceback.print_exc()
        return HTTPException(status_code=400, detail='Invalid data')


@app.delete('/bots/delete/')
async def delete_user(user_id: str):
    try:
        user = UserDB.filter_users(user_id=user_id)
        if len(user) == 0:
            return HTTPException(status_code=400, detail="User doesn't exist")
        main_queue.put(QueuedTask(UserDB, 'delete_user', {'user_id': user_id}))
        return {'Status': 'OK'}
    except Exception as ex:
        return HTTPException(status_code=400, detail="Server's unknown error")
