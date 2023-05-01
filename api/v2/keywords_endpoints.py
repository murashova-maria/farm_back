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

        # Возвращаем список ключевых слов и связанных с ними профилей пользователей
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
    keyword_id = int(keyword_id)
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
