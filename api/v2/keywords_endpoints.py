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
        keywords = KeywordDB.get_all_keywords_with_users()
        return [keyw for keyw in keywords]
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
async def update_keyword(keyword_id: str, params: Dict[Any, Any]):
    try:
        keyword_id = int(keyword_id)
        params.update({'keyword_id': keyword_id})
        main_queue.put(QueuedTask(KeywordDB, 'update_keyword', params))
        return {'Status': 'OK'}
    except ValueError:
        raise HTTPException(status_code=400, detail={'Status': 'Incorrect keyword ID or user_id'})
    except Exception as ex:
        raise HTTPException(status_code=400, detail={'Status': 'SERVER ERROR'})
