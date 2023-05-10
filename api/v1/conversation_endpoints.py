import traceback
from api import *
from random import choice, choices, shuffle


def unique_random_sublist(input_list, n):
    unique_elements = list(set(input_list))
    shuffle(unique_elements)
    if n > len(unique_elements):
        return unique_elements
    return unique_elements[:n]


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
                    r_usr = choice(params[acc_type])
                    if r_usr not in chain:
                        chain.append(r_usr)
                        break
            temp_data['tmp_data'].update({
                f'{post}': {
                    'index': 0,
                    'next_comment_date': params['start_datetime'],
                    'full_chain': chain
                    # 'full_chain': [choice(params['meek_accs']) if user['acc_type'] == 'meek'
                    #                else choice(params['master_accs'])
                    #                for user in params['thread']]
                } for post in params['post_links']
            })
        else:
            chain = []
            for _ in params['reactions']:
                for _ in range(3):
                    r_usr = choice([*params['meek_accs'], *params['master_accs']])
                    if r_usr not in chain:
                        chain.append(r_usr)
                        break

            temp_data['tmp_data'].update({
                f'{post}': {
                    'index': 0,
                    'next_comment_date': params['start_datetime'],
                    # 'full_chain': choices([*params['meek_accs'], *params['master_accs']], k=len(params['reactions']))
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
