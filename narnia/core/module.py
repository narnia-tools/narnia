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
        await self.injector.instantiate_all(self.params['behaviours'])
        await self.injector.instantiate_all(self.params['drivers'])

        behaviour = await self.injector.instantiate(behaviour_cls)
        while True:
            await behaviour.action()
            await asyncio.sleep(0.01)

        # behaviour_classes = self.params['bootstrap']
        #
        # actionable_behaviours = [b for b in behaviours if getattr(b, 'action', False)]
        #
        # async def action_loop():
        #     loop = asyncio.get_event_loop()
        #
        #     actions = [loop.create_task(behaviour.action()) for behaviour in actionable_behaviours]
        #
        #     while True:
        #         done, pending = await asyncio.wait(actions, return_when=asyncio.FIRST_COMPLETED)
        #         actions = [loop.create_task(actionable_behaviours[i].action()) if actions[i].done() else actions[i]
        #                    for i in range(len(actionable_behaviours))]

        await action_loop()

    def __call__(self, m):
        setattr(m, 'bootstrap', self.bootstrap)

        for driver in self.params['drivers']:
            self.injector.register(driver)

        for behaviour in self.params['behaviours']:
            self.injector.register(behaviour)

        return m
