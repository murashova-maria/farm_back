import json
import threading


class JSONWriter:
    def __init__(self, filename):
        self.filename = filename
        self.lock = threading.Lock()

    def write_json(self, data):
        with self.lock:
            try:
                with open(self.filename, 'w') as f:
                    json.dump(data, f)
            except IOError as e:
                print(f'Error writing JSON file: {e}')


class HandleConversationTest:
    def __init__(self):
        self.filename = 'conversations.json'

    def update_current_data(self, data):
        with open(self.filename, 'w') as output:
            output.write(data)
            # json.dump(data, output)


if __name__ == '__main__':
    pass
