import asyncio

from .injector import Injector

import time

INJECTOR = Injector()


class Module:
    def __init__(self, **params):
        self.injector = INJECTOR
        self.params = {
            **{
                'drivers': [],
                'behaviours': []
            },
            **params
        }

    async def bootstrap(self):
        behaviour_cls = self.params['bootstrap']
        default_behaviour = await self.injector.instantiate(behaviour_cls)

        drivers = await self.injector.instantiate_all(self.params['drivers'])
        drivers = [d for d in drivers if getattr(d, 'perceive', None) is not None]

        async def perception_loop():
            while True:
                # print('act loop', await drivers[0].perceive())
                proms = [d.perceive() for d in drivers if d is not None]
                print('x', proms)
                await asyncio.gather(*proms)
                time.sleep(0.05)

        async def action_loop():
            while True:
                await default_behaviour.action()

        await asyncio.gather(
            perception_loop(),
            action_loop()
        )


    def __call__(self, m):
        setattr(m, 'bootstrap', self.bootstrap)

        for driver in self.params['drivers']:
            self.injector.register(driver)

        for behaviour in self.params['behaviours']:
            self.injector.register(behaviour)

        return m
