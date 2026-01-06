from abc import ABC, abstractmethod


class OutputStrategy(ABC):
    @abstractmethod
    def output(self, data: dict):
        pass
