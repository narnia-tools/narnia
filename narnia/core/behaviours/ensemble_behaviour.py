from alibx.behaviours.behaviour import Behaviour

from random import random

class EnsembleBehaviour(Behaviour):

    def __init__(self, *ensemble):
        """
        Decides what model to use, i.e. Heat map or random chance.
        :param ensemble:
        """
        self.ensemble = ensemble

    def action(self, **senses):
        ptr = 0
        rnd = random()

        print('Coin Flip: ' + str(rnd))

        for behaviour, p in self.ensemble:
            ptr += p
            if ptr >= rnd:
                # self.inject_actuators(behaviour)
                print('Sampling using ' + behaviour.name())
                return behaviour.action(**senses)
