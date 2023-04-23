# OTHER
from time import sleep

# LOCAL
from loader import *
from farm.social_media.instagram import Instagram


def main(filename):
    instagram = Instagram('penguin_nube', '4cUrHjkF564UnJA')
    instagram.login()
    while True:
        instagram.collect_posts()
        sleep(1)
        input('>>> ')


if __name__ == '__main__':
    # node = UserDB.filter_users(user_id='9926be17-0c90-4be5-b84b-d6f061b57e79')[0]
    # local_graph.delete(node)
    usr_id = "d9ac0996-52a9-4c0a-beba-56634989020e"
    conv = Conversation(local_graph)
    conv.add_user_to_chat(30, usr_id)
    conv.add_message_to_user(chat_id=30, user_id=usr_id, message_text='new text', delay=10)
    print(conv.get_chat_info(30))
