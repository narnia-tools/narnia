from abc import ABC, abstractmethod
import asyncio

@asyncio.coroutine
def action(f):
    def wrapper(*args):
        print(args[0])
        return {
            action: f(*args)
        }

    return wrapper


class Actuator(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def push(self):
        pass
