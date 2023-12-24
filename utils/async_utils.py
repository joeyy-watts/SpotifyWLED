import asyncio
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
    def run(self):
        """
        Runs the coroutine function.

        This is a blocking function that will spawn tasks to run the required loops

        :return: the asyncio.Task that is running the coroutine function
        """
        self.loop.create_task(self.__stop_loop())
        return self.loop.create_task(self.__main_loop())

    @final
    def stop(self):
        """
        Stops the coroutine function manually.
        """
        self.stop_event.set()

    async def _main_function(self):
        """
        Main logic of the coroutine function should be implemented here.
        """
        raise NotImplementedError

    async def _stop_function(self):
        """
        Function to determine whether the coroutine should stop.

        This function should call self.stop_event.set() when the coroutine should stop.
        """
        raise NotImplementedError

    @final
    async def __stop_loop(self):
        while not self.stop_event.is_set():
            await asyncio.sleep(POLLING_SECONDS)
            await self._stop_function()

    @final
    async def __main_loop(self):
        while not self.stop_event.is_set():
            await self._main_function()
