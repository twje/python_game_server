class Message:
    def __init__(self, data):
        self.data = data

    @property
    def event_type(self):
        return self.data["event_type"]
