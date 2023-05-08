# LOCAL
from api import *

# OTHER
from time import sleep


@app.post('/keywords/')
async def add_keywords(params: Dict[Any, Any]):
    try:
        additional_params = {}
        keyword = params.get('keyword_value')
        if keyword.get('twitter'):
            additional_params.update({'twitter_user': keyword.get('twitter')})
        if keyword.get('facebook'):
            additional_params.update({'facebook_user': keyword.get('facebook')})
        if keyword.get('instagram'):
            additional_params.update({'instagram_user': keyword.get('instagram')})
        main_queue.put(QueuedTask(KeywordDB, 'create_keyword', {'keyword': keyword, **additional_params}))
        return {'Status': 'OK'}
    except Exception as ex:
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})


@app.get('/keywords/')
async def get_keywords():
    try:
        result = []
        all_keywords = KeywordBase().get_all_keywords()
        for keyword in all_keywords:
            if keyword['facebook_user']:
                fb_user = UserBase.filter_users(user_id=keyword['facebook_user'])[0]
                keyword.update({'facebook': fb_user})
            if keyword['instagram_user']:
                inst_user = UserBase.filter_users(user_id=keyword['instagram_user'])[0]
                keyword.update({'instagram': inst_user})
            if keyword['twitter_user']:
                tw_user = UserBase.filter_users(user_id=keyword['twitter_user'])[0]
                keyword.update({'twitter': tw_user})
            result.append(keyword)
        return result
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})


@app.delete('/bots/{user_id}/keywords/{keyword_id}/')
async def unpin_word_from_user(user_id: str, keyword_id: str):
    try:
        keyword_id = int(keyword_id)
        main_queue.put(QueuedTask(KeywordDB, 'unpin_keyword_from_user', {
            'keyword_id': keyword_id,
            'user_id': user_id
        }))
        return {'Status': 'OK'}
    except ValueError:
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})
    except Exception as ex:
        raise HTTPException(status_code=400, detail={'Status': 'SERVER ERROR'})


@app.delete('/keywords/{keyword_id}/')
async def delete_keyword(keyword_id: str):
    try:
        keyword_id = int(keyword_id)
        main_queue.put(QueuedTask(KeywordDB, 'delete_keyword',
                                  {'keyword_id': keyword_id}))
        KeywordDB.delete_keyword(keyword_id)
        return {'Status': 'OK'}
    except ValueError:
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})
    except Exception as ex:
        raise HTTPException(status_code=400, detail={'Status': 'SERVER ERROR'})


@app.put('/keywords/{keyword_id}/')
async def update_keyword(keyword_id: str | int, params: Dict[Any, Any]):
    try:
        keyword_id = int(keyword_id)
        keyword_obj = KeywordDB.filter_keywords(keyword_id=keyword_id)
        if not keyword_obj:
            return
        for key, value in params.items():
            main_queue.put(QueuedTask(KeywordDB, 'add_keyword_to_user', {
                'keyword_id': keyword_id,
                'user_id': value,
                'network': key
            }))
        return {'Status': 'OK'}
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail={'Status': 'SERVER ERROR'})
