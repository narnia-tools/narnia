from abc import ABC, abstractmethod
import asyncio
class Behaviour(ABC):

    def __init__(self):
        self.actuators = {}

    def name(self):
        return type(self).__name__

    def __str__(self):
        return self.name()

    def inject_actuators(self, behaviour):
        behaviour = self.actuators

    @abstractmethod
    def action(self, **senses):
        """
        :param control: status (x, y, z, alpha, pa, pb, pc, ca, cb, cc)
        :param perception: current frames, i.e., pair of images (left,right)
        :return: (x, y, z, alpha, amplitude)
        """
        raise NotImplementedError

    async def start(self, action, **senses):
        return asyncio.run(action(**senses))
