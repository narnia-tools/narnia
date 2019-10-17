class Module:
    def __init__(self, **kwargs):
        print(self, kwargs)
        # self.params = dict({'topic': topic}, **kwargs)

    def __call__(self, m):
        self.m = m



