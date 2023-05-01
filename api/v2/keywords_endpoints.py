# LOCAL
from api import *


@app.post('/keywords/')
async def add_keywords(params: Dict[Any, Any]):
    try:
        main_queue.put(QueuedTask(KeywordDB, 'add_keyword_to_user', params))
        return {'Status': 'OK'}
    except Exception as ex:
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})


@app.get('/keywords/')
async def get_keywords():
    try:
        tmp = []
        general = []
        keywords = KeywordDB.get_all_keywords_with_users()
        for keyw in keywords:
            twitter_profile = []
            facebook_profile = []
            instagram_profile = []
            for user in keyw['users']:
                if user['social_media'] == 'twitter':
                    twitter_profile.append(user)
                elif user['social_media'] == 'facebook':
                    facebook_profile.append(user)
                else:
                    instagram_profile.append(user)
            if facebook_profile:
                keyw.update({'facebook': facebook_profile[0]})
            if twitter_profile:
                keyw.update({'twitter': twitter_profile[0]})
            if instagram_profile:
                keyw.update({'instagram': instagram_profile[0]})
            general.append(keyw)
            keyw.pop('users')
        for word in KeywordDB.get_all_keywords():
            for s_word in general:
                if word.get('keyword') != s_word.get('keyword'):
                    tmp.append({key: value for key, value in word.items()})
        return [x for x in [*general, *tmp] if x.get('keyword') != 'scroll_feed']
        # return [keyw for keyw in keywords]
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})


@app.delete('/bots/{user_id}/keywords/{keyword_id}/')
async def unpin_word_from_user(user_id: str, keyword_id: str):
    try:
        keyword_id = int(keyword_id)
        KeywordDB.unpin_word_from_user(user_id, keyword_id)
        return {'Status': 'OK'}
    except ValueError:
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})
    except Exception as ex:
        raise HTTPException(status_code=400, detail={'Status': 'SERVER ERROR'})


@app.delete('/keywords/{keyword_id}/')
async def delete_keyword(keyword_id: str):
    try:
        keyword_id = int(keyword_id)
        KeywordDB.delete_keywords(keyword_id)
        return {'Status': 'OK'}
    except ValueError:
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})
    except Exception as ex:
        raise HTTPException(status_code=400, detail={'Status': 'SERVER ERROR'})


@app.put('/keywords/{keyword_id}/')
async def update_keyword(keyword_id: str | int, params: Dict[Any, Any]):
    keyword_id = int(keyword_id)
    kw_value = None
    to_delete = []
    try:
        for keyword in KeywordDB.get_all_keywords_with_users():
            if keyword_id != keyword['keyword_id']:
                continue
            kw_value = keyword['keyword_value']
            for user in keyword['users']:
                for key, value in params.items():
                    if key == user['social_media']:
                        to_delete.append(user['user_id'])
                    if value is not None:
                        main_queue.put(QueuedTask(KeywordDB, 'update_keyword_for_user', {'keyword': kw_value,
                                                                                         'social_media': key,
                                                                                         'user_id': value}))
        for to_be_deleted in to_delete:
            main_queue.put(QueuedTask(KeywordDB, 'unpin_word_from_user', {'keyword_id': keyword_id,
                                                                             'user_id': to_be_deleted}))
        return {'Status': 'OK'}
    except ValueError:
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})
    except Exception as ex:
        raise HTTPException(status_code=400, detail={'Status': 'SERVER ERROR'})
