from .injectable import Injectable

class Driver(Injectable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
