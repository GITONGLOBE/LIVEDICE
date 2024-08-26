from abc import ABC, abstractmethod

class UIInterface(ABC):
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update_leaderboard_scroll(self):
        pass