# OTHER
from time import sleep

# LOCAL
from loader import *


if __name__ == '__main__':
    for user in FacebookProfileDB.get_all():
        print(user)
        print()
    # local_graph.delete_all()
