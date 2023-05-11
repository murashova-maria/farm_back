# OTHER
from time import sleep

# LOCAL
from loader import *


if __name__ == '__main__':
    all_keywords = KeywordBase().get_all_keywords()
    for word in all_keywords:
        print(word)
