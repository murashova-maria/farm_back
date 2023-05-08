from api import *
from random import choice, choices
import traceback


@app.post('/conversation/create/')
async def create_conversation(params: Dict[Any, Any]):
    temp_data = {'tmp_data': {}}
    params.update({'start_datetime': datetime.now().timestamp()})
    conversation_id = randint(0, 2147483647)
    try:
        if 'thread' in params:
            temp_data['tmp_data'].update({
                f'{post}': {
                    'index': 0,
                    'next_comment_date': params['start_datetime'],
                    'full_chain': [choice(params['meek_accs']) if user['acc_type'] == 'meek'
                                   else choice(params['master_accs'])
                                   for user in params['thread']]
                } for post in params['post_links']
            })
        else:
            temp_data['tmp_data'].update({
                f'{post}': {
                    'index': 0,
                    'next_comment_date': params['start_datetime'],
                    'full_chain': choices([*params['meek_accs'], *params['master_accs']], k=len(params['reactions']))
                } for post in params['post_links']
            })
        params.update(temp_data)
        params = {conversation_id: {**params, 'type': 'json'}, }
        res = read_json('conversations.json')
        res.update(params)
        JSONWriter('conversations.json').write_json(res)
        return {'Status': 'OK'}
    except Exception as ex:
        print(ex)
        return HTTPException(status_code=400, detail='Wrong data')
