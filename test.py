# OTHER
from time import sleep

# LOCAL
from loader import *
from farm.social_media.instagram import Instagram


if __name__ == '__main__':
    usr_id = "742f3cd1-503a-4ee3-bb62-0699a9262760"
    u = Keyword(local_graph)
    print(u.get_all_keywords())
