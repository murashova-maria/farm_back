# OTHER
from time import sleep

# LOCAL
from farm.social_media.instagram import Instagram


def main(filename):
    instagram = Instagram('penguin_nube', '4cUrHjkF564UnJA')
    instagram.login()
    while True:
        instagram.collect_posts()
        sleep(1)
        input('>>> ')


if __name__ == '__main__':
    file = '/home/penguin_nube/Pictures/Screenshot_20230307_192541.png'
    main(file)
    input('>>> ')
