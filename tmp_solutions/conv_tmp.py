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


class HandleConversationTest:
    def __init__(self):
        self.filename = 'conversations.json'
        self.output = open(self.filename, 'w')

    def __del__(self):
        self.output.close()

    def test_dump(self):
        json.dump({}, self.output)
        self.output.flush()

    def update_current_data(self, data):
        json.dump(data, self.output)
        self.output.flush()


if __name__ == '__main__':
    pass
