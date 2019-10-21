from .injectable import Injectable

class Behaviour(Injectable):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

