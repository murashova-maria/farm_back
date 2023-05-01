import json


class HandleConversation:
    def __init__(self, result):
        self.filename = 'conversations.json'
        self.result = result

    def test_dump(self):
        with open(self.filename, 'w') as output:
            json.dump({}, output)
            output.close()

    def update_current_data(self, data):
        with open(self.filename, 'w') as output:
            self.result.update(data)
            json.dump(self.result, output)
            output.close()


if __name__ == '__main__':
    h = HandleConversation()
    h.test_dump()
