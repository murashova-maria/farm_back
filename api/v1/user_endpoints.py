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


@app.get('/bots/all/info/')
async def get_all_users():
    users = UserDB.get_all()
    general_data = []
    for user in users:
        general_data.append({key: value for key, value in user.items()})
    if general_data:
        return general_data
    raise HTTPException(status_code=400, detail='Database is empy')


@app.get('/bots/all/profiles/')
async def get_all_users_profiles():
    data = {
        'twitter': {},
        'facebook': {},
        'instagram': {}
    }
    social_media = [TwitterProfileDB.get_all(),
                    FacebookProfileDB.get_all(),
                    InstagramProfileDB.get_all()]
    for index, media in enumerate(social_media):
        net = 'twitter' if index == 0 else 'facebook' if index == 1 else 'instagram'
        for profile in media:
            data[net].update({profile['user_id']: {
                key: value for key, value in profile.items() if key != 'user_id'
            }})
    if data:
        return data
    raise HTTPException(status_code=400, detail='Database is empy')


@app.get('/bots/{user_id}/info/')
async def read_account(user_id: str):
    usr = UserDB.filter_users(user_id=user_id)
    if usr is None:
        raise HTTPException(status_code=404, detail='User not found')
    usr = usr[0]
    twitter_profile = TwitterProfileDB.filter_profiles(user_id=user_id)
    facebook_profile = FacebookProfileDB.filter_profiles(user_id=user_id)
    instagram_profile = InstagramProfileDB.filter_profiles(user_id=user_id)
    data = {
        'user_info': {key: value for key, value in usr.items()},
        'profile_info': {},
    }
    if twitter_profile:
        data['profile_info'].update({'twitter_profile': {
            key: value for key, value in twitter_profile[0].items()}
        })
    if facebook_profile:
        data['profile_info'].update({'facebook_profile': {
            key: value for key, value in facebook_profile[0].items()}
        })
    if instagram_profile:
        data['profile_info'].update({'instagram_profile': {
            key: value for key, value in instagram_profile[0].items()}
        })
    return data


@app.put("/bots/{user_id}/info/")
async def update_account(user_id: str, item: Dict[Any, Any]):
    usr = UserDB.filter_users(user_id=user_id)[0]
    if usr is None:
        raise HTTPException(status_code=404, detail='User not found')
    data_to_update = {key: value for key, value in item.items() if key in usr}
    data_to_update.update({'user_id': user_id})
    main_queue.put(QueuedTask(UserDB, 'update_user', data_to_update))
    return {'Success': 'Database updated successfully'}


@app.put('/bots/{user_id}/profile/')
async def update_profile(user_id: str, item: Dict[Any, Any]):
    item.update({'user_id': user_id})
    network = UserDB.filter_users(user_id=user_id)
    for key, value in item.items():
        if key != 'filename':
            continue

    if network:
        network = network[0]['social_media']
    else:
        return {'Error': 'Invalid user_id'}
    if network == 'twitter':
        profile_object = TwitterProfileDB
    elif network == 'facebook':
        profile_object = FacebookProfileDB
    else:
        profile_object = InstagramProfileDB
    if not profile_object:
        raise HTTPException(status_code=404, detail='Invalid user')
    social_media = UserDB.filter_users(user_id=user_id)[0]['social_media']
    if 'avatar' in item:
        image = item.get('avatar')
        if image:
            extension, image = image.split(',')
            if 'jpg' in extension or 'jpeg' in extension:
                filename = f'{user_id}_avatar_{randint(0, 10000)}.jpg'
            else:
                filename = f'{user_id}_avatar_{randint(0, 10000)}.png'
            image = base64.b64decode(image)
            with open(IMG_DIR + f'{social_media}/' + filename, 'wb') as output:
                output.write(image)
            item['avatar'] = filename
    if 'cover' in item:
        image = item.get('cover')
        if image:
            extension, image = image.split(',')
            if 'jpg' in extension or 'jpeg' in extension:
                filename = f'{user_id}_cover_{randint(0, 10000)}.jpg'
            else:
                filename = f'{user_id}_cover_{randint(0, 10000)}.png'
            image = base64.b64decode(image)
            with open(IMG_DIR + f'{social_media}/' + filename, 'wb') as output:
                output.write(image)
            item['cover'] = filename
    main_queue.put(QueuedTask(profile_object, 'update_profile', item))
    return {'Success': 'Database updated successfully'}
