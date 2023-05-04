from api import *
from random import choice, choices
import traceback


# @app.post('/conversation/create/')
# async def create_conversation(params: Dict[Any, Any]):
#     try:
#         temp_data = {'tmp_data': {}}
#         timestamp = params.get('start_date_time')
#         new_conversation = ConversationsPostgres()
#         new_conversation.conversation_id = randint(0, 2147483647)
#         new_conversation.conversation_name = params.get('campaign_name')
#         new_conversation.post_links = params.get('post_links')
#         new_conversation.master_accounts = params.get('master_accs')
#         new_conversation.meek_accounts = params.get('meek_accs')
#         new_conversation.start_datetime = timestamp
#         new_conversation.tmp_data = params.get('tmp_data')
#         if 'thread' in params:
#             new_conversation.thread = params.get('thread')
#             temp_data['tmp_data'].update({
#                 f'{post}': {
#                     'index': 0,
#                     'next_comment_date': timestamp,
#                     'full_chain': [choice(params['meek_accs']) if user['acc_type'] == 'meek'
#                                    else choice(params['master_accs'])
#                                    for user in params['thread']]
#                 } for post in params['post_links']
#             })
#         else:
#             new_conversation.reactions = params.get('reactions')
#             temp_data['tmp_data'].update({
#                 f'{post}': {
#                     'index': 0,
#                     'next_comment_date': timestamp,
#                     'full_chain': choices([*params['meek_accs'], *params['master_accs']], k=len(params['reactions']))
#                 } for post in params['post_links']
#             })
#         new_conversation.tmp_data = temp_data['tmp_data']
#         user_session.add(new_conversation)
#         user_session.commit()
#         return {'Status': 'OK'}
#     except Exception as ex:
#         traceback.print_exc()
#         return HTTPException(status_code=400, detail='Wrong data')


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
        main_queue.put(QueuedTask(HandleConversation(read_json()), 'update_current_data', params))
        return {'Status': 'OK'}
    except Exception as ex:
        print(ex)
        return HTTPException(status_code=400, detail='Wrong data')
