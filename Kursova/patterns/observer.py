class Observer:
    def update(self, message):
        pass


class NotificationObserver(Observer):
    def update(self, message):
        print("NOTIFICATION:", message)


class Subject:
    def __init__(self):
        self.observers = []

    def attach(self, obs):
        self.observers.append(obs)

    def notify(self, message):
        for o in self.observers:
            o.update(message)
