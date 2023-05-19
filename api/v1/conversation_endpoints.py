import traceback
from api import *
from random import choice
from api.utils import save_base64_file


@app.post('/conversation/create/')
async def create_conversation(params: Dict[Any, Any]):
    temp_data = {'tmp_data': {}}
    params.update({'start_datetime': datetime.now().timestamp()})
    conversation_id = randint(0, 2147483647)
    try:
        if 'thread' in params:
            chain = []
            for user in params['thread']:
                acc_type = user['acc_type']
                for _ in range(3):
                    r_usr = choice(params[acc_type + '_accs'])
                    if r_usr not in chain:
                        chain.append(r_usr)
                        break
                base_image = user.get('image')
                if base_image:
                    user['image'] = save_base64_file(base_image)
            temp_data['tmp_data'].update({
                f'{post}': {
                    'index': 0,
                    'next_comment_date': params['start_datetime'],
                    'full_chain': chain
                } for post in params['post_links']
            })
        else:
            chain = []
            for reaction in params['reactions']:
                for _ in range(3):
                    r_usr = choice([*params['meek_accs'], *params['master_accs']])
                    if r_usr not in chain:
                        chain.append(r_usr)
                        break
                if reaction.get('image'):
                    reaction['image'] = save_base64_file(reaction['image'])
            temp_data['tmp_data'].update({
                f'{post}': {
                    'index': 0,
                    'next_comment_date': params['start_datetime'],
                    'full_chain': chain
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
