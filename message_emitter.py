from collections import defaultdict

__all__ = ["MessageEmitter"]


class Communicator:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        if observer in self.observers:
            return False
        self.observers.append(observer)
        return True

    def remove_observer(self, observer):
        if observer not in self.observers:
            return False
        self.observers.remove(observer)
        return True

    def broadcast(self, message):
        for observer in self.observers:
            observer.notify(message.event_type, message)


class MessageEmitter:
    def __init__(self):
        self.communicators = defaultdict(Communicator)

    def subscribe(self, event_type, observer):
        communicator = self.communicators[event_type]
        return communicator.add_observer(observer)

    def unsubscribe(self, event_type, observer):
        communicator = self.communicators[event_type]
        return communicator.remove_observer(observer)

    def dispatch(self, message):
        communicator = self.communicators[message.event_type]
        communicator.broadcast(message)
