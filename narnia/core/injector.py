import asyncio

loop = asyncio.get_event_loop()


class Injector():

    def __init__(self):
        self.injectables = {}
        self.instances = {}

    def get(self, cls):
        if cls in self.instances:
            return self.instances[cls]
        return None

    def get_all(self, clss):
        return [self.get(c) for c in clss]

    def register(self, cls):
        dependencies = cls.__depedendencies__
        self.injectables[cls] = dependencies

    def new(self, cls):
        self.instances[cls] = self.instances[cls] if cls in self.instances else cls()
        return self.instances[cls]

    async def instantiate(self, cls):

        spec = self.injectables[cls]
        instance = self.new(cls)

        for attr, dep_cls in spec.items():
            dep_instance = self.new(dep_cls)
            setattr(instance, attr, dep_instance)

        if getattr(instance, 'after_init', False):
            x = instance.after_init()
            if x is not None:
                await x

        return instance

    async def instantiate_all(self, clss):
        return await asyncio.gather(*tuple([self.instantiate(x) for x in clss]))
    # if cls in self.instances:
    # else:
    #     self.instances[cls] = self.instantiate(cls)
    #     return self.instances[cls]

    # def register(self, cls):
    #     # self.units[cls] =
    #     pass

    # def register_all(self, ):
