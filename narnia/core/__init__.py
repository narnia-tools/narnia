from .behaviours import *
from .drivers import *
from .module import Module
from .narnia import Narnia

from .behaviour import Behaviour
from .driver import Driver
from .multi_step_action import MultiStepAction

from asyncio import get_event_loop
from functools import partial
from time import time

import asyncio

__request_id_counter__ = 1


def RequestAction(self, goal):
    global __request_id_counter__

    request = getattr(self, '__request__', False)

    if request and not request['future'].done():
        request['future'].set_result('INTERRUPTED')

    __request_id_counter__ += 1
    req_id = __request_id_counter__
    new_request = {
        'future': get_event_loop().create_future(),
        'goal': partial(goal, time()),
        'timestamp': time(),
        'id': req_id
    }

    setattr(self, '__request__', new_request)

    loop = asyncio.get_event_loop()
    loop.create_task(__verify_request__(self, req_id))

    return new_request['future']


async def __verify_request__(self, id):
    await asyncio.sleep(0.03)

    request = getattr(self, '__request__', False)
    if request and request['id'] == id:
        if not request['future'].done():
            cond = request['goal'](time())
            if cond:
                request['future'].set_result('DONE')
            elif (time() - request['timestamp']) > 15:
                request['future'].set_result('FAILED')
            else:
                await __verify_request__(self, id)

# def RefreshAction(self):
#     request = getattr(self, '__request__', False)
#     if request:
#         if not request['future'].done():
#             print('>', time())
#             cond = request['goal'](time())
#             if cond:
#                 request['future'].set_result('DONE')
#             elif (time() - request['timestamp']) > 15:
#                 request['future'].set_result('FAILED')
#         else:
#             delattr(self, '__request__')
