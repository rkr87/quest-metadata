"""
Module providing an asynchronous runner for executing synchronous methods in
a separate thread.

Classes:
- AsyncRunner: Final class for running synchronous methods asynchronously using
    an event loop.

Attributes:
- _T: TypeVar representing the return type of the synchronous method.
"""
from asyncio import AbstractEventLoop, Future, get_event_loop
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, TypeVar, final

_T = TypeVar("_T")


@final
class AsyncRunner:
    """
    Final class for running synchronous methods asynchronously using an
    event loop.

    Attributes:
    - _pool (ThreadPoolExecutor): Thread pool for executing synchronous
        methods.

    Methods:
    - __init__: Initialize the AsyncRunner with an optional thread pool.
    - call: Asynchronously call a synchronous method with arguments and
        keyword arguments.
    """

    def __init__(
        self,
        pool: ThreadPoolExecutor | None = None
    ) -> None:
        self._pool: ThreadPoolExecutor = pool or ThreadPoolExecutor()

    async def call(
        self,
        method: Callable[..., _T],
        *args: Any,
        **kwargs: Any
    ) -> _T:
        """
        Asynchronously call a synchronous method with arguments and keyword
        arguments.

        Args:
        - method (Callable[..., _T]): Synchronous method to be executed.
        - *args (Any): Variable-length argument list.
        - **kwargs (Any): Variable-length keyword argument list.

        Returns:
        - _T: Result of the synchronous method.

        Example:
        ```python
        def sync_method(arg: int, kwarg: bool = False) -> str:
            # Some synchronous logic
            return f"Result: {arg}, {kwarg}"

        async_runner = AsyncRunner()
        result = await async_runner.call(sync_method, 42, kwarg=True)
        print(result)
        ```
        """
        loop: AbstractEventLoop = get_event_loop()
        future: Future[_T] = loop.run_in_executor(
            self._pool,
            partial(method, **kwargs),
            *args
        )
        return await future
