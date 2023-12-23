import asyncio
from asyncio import Event
from typing import final

from confs.global_confs import POLLING_SECONDS


class ManagedCoroutineFunction:
    """
    Base class for managing coroutine functions.

    Subclasses should implement the following:
        - _main_function: the main logic of the coroutine function
        - _stop_function: the function that determines when the coroutine should stop

    The coroutine will stop in the following cases:
        - _stop_function calls stop_event.is_set()
        - stop() is called
    """
    def __init__(self):
        """
        Any parameters needed for the coroutine function should be passed and initialized here.

        super().__init__(*args, **kwargs) must be used in the subclass.
        """
        self.stop_event = asyncio.Event()
        self.loop = asyncio.get_event_loop()

    @final
    async def run(self, *args, **kwargs):
        """
        Runs the coroutine function.
        """
        self.loop.create_task(self.__stop_loop(self.stop_event))

        while not self.stop_event.is_set():
            await self._main_function(*args, **kwargs)

    @final
    async def stop(self):
        """
        Stops the coroutine function manually.
        """
        self.stop_event.set()

    async def _main_function(self, *args, **kwargs):
        """
        Main logic of the coroutine function should be implemented here.
        """
        raise NotImplementedError

    async def _stop_function(self, stop_event: Event):
        """
        Function to determine whether the coroutine should stop.

        This function should call stop_event.set() when the coroutine should stop.
        """
        raise NotImplementedError

    @final
    async def __stop_loop(self, stop_event: Event):
        while not stop_event.is_set():
            await asyncio.sleep(POLLING_SECONDS)
            await self._stop_function(stop_event)
