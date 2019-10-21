import inspect

def get_annotations(cls):
    annotations = [t[1] for t in inspect.getmembers(cls) if t[0] == '__annotations__']
    if len(annotations) > 0:
        return annotations[0]
    return {}


class Injectable:

    def __init__(self, **params):
        self.params = params

    def __call__(self, cls):
        cls.__depedendencies__ = get_annotations(cls)
        return cls
