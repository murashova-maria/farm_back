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
        all_keywords = KeywordDB.get_all_keywords()
        # Получаем все ключевые слова и связанные с ними профили пользователей
        keywords = KeywordDB.get_all_keywords_with_users()

        # Создаем словарь для хранения ключевых слов и связанных с ними профилей пользователей
        result = {}

        # Добавляем каждое ключевое слово и связанные с ними профили пользователей в словарь
        for keyword in keywords:
            keyword_name = keyword['keyword']
            users = keyword.pop('users')

            # Создаем список профилей пользователей для каждой социальной сети
            twitter_profiles = []
            facebook_profiles = []
            instagram_profiles = []

            # Группируем профили пользователей по социальным сетям
            for user in users:
                if user['social_media'] == 'twitter':
                    twitter_profiles.append(user)
                elif user['social_media'] == 'facebook':
                    facebook_profiles.append(user)
                elif user['social_media'] == 'instagram':
                    instagram_profiles.append(user)

            # Добавляем первый профиль пользователя для каждой социальной сети к ключевому слову
            if facebook_profiles:
                keyword['facebook'] = facebook_profiles[0]
            if twitter_profiles:
                keyword['twitter'] = twitter_profiles[0]
            if instagram_profiles:
                keyword['instagram'] = instagram_profiles[0]

            # Добавляем ключевое слово и связанные с ним профили пользователей в словарь
            result[keyword_name] = keyword
        for keyw in all_keywords:
            if keyw['keyword'] not in result:
                result.update({keyw['keyword']: {key: value for key, value in keyw.items()}})
        return list(result.values())
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
    try:
        keyword_id = int(keyword_id)
        keyword_obj = KeywordDB.filter_keywords(keyword_id=keyword_id)
        if not keyword_obj:
            return {'Status': 'WRONG KEYWORD ID'}
        keyword_obj = keyword_obj[0]
        all_keywords = [*KeywordDB.get_all_keywords_with_users(), *KeywordDB.get_all_keywords()]
        for keyword in all_keywords:
            if int(keyword['keyword_id']) != keyword_id:
                continue
            if keyword['users'] is None:
                for key, value in params.items():
                    main_queue.put(QueuedTask(KeywordDB, 'add_keyword_to_user', [keyword['keyword'], value]))
                    # KeywordDB.add_keyword_to_user(keyword_obj['keyword'], value)
                continue
            for user in keyword['users']:
                if user['social_media'] in params:
                    if params[user['social_media']]:
                        main_queue.put(QueuedTask(KeywordDB, 'unpin_word_from_user', [keyword['keyword'], keyword_id]))
                        # KeywordDB.unpin_word_from_user(user['user_id'], keyword_id)
                    main_queue.put(QueuedTask(KeywordDB, 'add_keyword_to_user', [keyword['keyword'],
                                                                                 params[user['social_media']]]))
                    # KeywordDB.add_keyword_to_user(keyword_obj['keyword'], params[user['social_media']])

        all_keywords = [*KeywordDB.get_all_keywords_with_users(), *KeywordDB.get_all_keywords()]
        for keyword in all_keywords:
            if int(keyword['keyword_id']) != keyword_id:
                continue
            for key, value in params.items():
                if value is None:
                    if keyword['users'] is None:
                        continue
                    for user in keyword['users']:
                        if user['social_media'] != key:
                            continue
                        main_queue.put(QueuedTask(KeywordDB, 'unpin_word_from_user', [user['user_id'],
                                                                                      keyword['keyword_id']]))
                        # KeywordDB.unpin_word_from_user(user['user_id'], keyword['keyword_id'])
        return {'Status': 'OK'}
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail={'Status': 'SERVER ERROR'})
