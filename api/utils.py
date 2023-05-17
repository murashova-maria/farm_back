# LOCAL
from loader import DATE_FORMAT, IMG_DIR

# DATE
from datetime import datetime

import base64
from random import randint


def ready_to_post(date):
    if date == 'now':
        return True
    if type(date) is str:
        date = datetime.strptime(date, DATE_FORMAT)
    return date <= datetime.now()

def save_base64_file(image):
    
    extension, image = image.split(',')
    filename = f'comment_image_{randint(0, 10000)}.jpg'
    image = base64.b64decode(image)
    with open(IMG_DIR + f'comment_images/' + filename, 'wb') as output:
        output.write(image)
    return filename


if __name__ == '__main__':
    pass
