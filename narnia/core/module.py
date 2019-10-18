class Module:
    def __init__(self, **params):
        self.params = params

    def __call__(self, m):
        setattr(m, 'bootstrap', self.params['bootstrap'])
        return m
