# OTHER
from time import sleep

# LOCAL
from loader import *


if __name__ == '__main__':
    # KeywordDB.unpin_word_from_user('f49701a5-52e0-45c4-90d3-3505f30f32df', 71104838)
    # for keyword in KeywordDB.get_all_keywords_with_users():
    #     print(keyword)
    #     local_graph.delete(keyword)
        # if keyword['keyword'] != 'Nord-Kivu' and keyword['keyword'] != 'ΣΥΡΙΖΑ':

    # conversations = ConversationDB.get_all()
    # for conv in conversations:
    #     print(conv)
    for profile in TwitterProfileDB.filter_profiles(user_id='c6d62287-9375-4aa8-b7ce-dae3127211c5'):
        local_graph.delete()
    # users = UserDB.filter_users(user_id="af2e3017-5be7-41d6-aea4-0767be11af33")
    # for user in users:
    #     local_graph.delete(user)
    pass
