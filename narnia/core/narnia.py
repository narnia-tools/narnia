import asyncio

class Narnia:
    @staticmethod
    def bootstrap(module):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(module.bootstrap())

