# OTHER
from time import sleep

# LOCAL
from loader import *


if __name__ == '__main__':
    for keyword in KeywordDB.get_all_keywords():
        print(keyword)
    #     local_graph.delete(keyword)
        # if keyword['keyword'] != 'Nord-Kivu' and keyword['keyword'] != 'ΣΥΡΙΖΑ':

    # conversations = ConversationDB.get_all()
    # for conv in conversations:
    #     print(conv)
    # users = UserDB.filter_users(social_media='facebook')
    # for user in users:
    #     local_graph.delete(user)
    # pass
