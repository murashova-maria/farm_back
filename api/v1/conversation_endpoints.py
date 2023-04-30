from api import *
from random import choice, choices


@app.post('/conversation/create/')
async def create_conversation(params: Dict[Any, Any]):
    conversation_id = randint(0, 2147483647)
    try:
        if 'thread' in params.keys():
            temp_data = {
                'tmp_data': {
                    f'{post}': {
                        'index': 0,
                        'next_time_message': params['start_datetime'],
                        'chain': [choice(params['master_accs']), *choices(params['meek_accs'],
                                                                          k=len(params['thread'])-1)],
                    } for post in params['post_links']
                }
            }
        else:
            temp_data = {
                'tmp_data': {
                    f'{post}': {
                        'index': 0,
                        'next_time_message': params['start_datetime'],
                        'chain': [choice(params['master_accs']), *choices(params['meek_accs'],
                                                                          k=len(params['reactions'])-1)],
                    } for post in params['post_links']
                }
            }
        params.update(temp_data)
        params = {conversation_id: {**params}}
        main_queue.put(QueuedTask(HandleConversation(read_json()), 'update_current_data', params))
        return {'Status': 'OK'}
    except Exception as ex:
        print(ex)
        return HTTPException(status_code=400, detail='Wrong data')


@app.put('/conversation/{conversation_id}/')
async def add_user_to_conversation():
    pass


@app.put('/conversation/{conversation_id}/{user_id}/')
async def add_message_to_user():
    pass
