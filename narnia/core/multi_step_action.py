from functools import wraps

class MultiStepAction():

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gen = None

    def __call__(self, fn):

        @wraps(fn)
        async def wrapped(fn_self, *fn_args, **fn_kwargs):
            if self.gen is None:
                self.gen = fn(fn_self, *fn_args, *fn_kwargs)

            try:
                await self.gen.__anext__()
            except StopAsyncIteration:
                self.gen = fn(fn_self, *fn_args, *fn_kwargs)
                await self.gen.__anext__()

        return wrapped