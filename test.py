# OTHER
from time import sleep

# LOCAL
from loader import *


if __name__ == '__main__':
    for conv in user_session.query(ConversationsPostgres).all():
        conv.tmp_data['https://www.facebook.com/groups/2153777644688768/permalink/6249143518485473']['index'] += 1
        print(conv.tmp_data)
        # user_session.add(conv)
        # user_session.commit()
    # conversations = read_json()
    # for key, conv in conversations.items():
    #     new_conversation = ConversationsPostgres()
    #     new_conversation.conversation_id = key
    #     new_conversation.conversation_name = conv['campaign_name']
    #     new_conversation.post_links = conv['post_links']
    #     new_conversation.master_accounts = conv['master_accs']
    #     new_conversation.meek_accounts = conv['meek_accs']
    #     new_conversation.start_datetime = datetime.datetime.now()
    #     new_conversation.tmp_data = conv['tmp_data']
    #     new_conversation.thread = conv['thread']
    #     user_session.add(new_conversation)
    #     user_session.commit()
    pass
