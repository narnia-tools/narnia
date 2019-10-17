from abc import ABC, abstractmethod


class Behaviour(ABC):

    @abstractmethod
    def action(self, **senses):
        """
        :param control: status (x, y, z, alpha, pa, pb, pc, ca, cb, cc)
        :param perception: current frames, i.e., pair of images (left,right)
        :return: (x, y, z, alpha, amplitude)
        """
        raise NotImplementedError
