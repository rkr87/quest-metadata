# pyright: reportMissingTypeArgument=false
"""
Module: http_client

Description:
    This module provides an asynchronous HTTP client using the aiohttp library.
    The HttpClient class supports opening and closing client sessions with
    configurable connection limits.

Example:
    ```python
        client = http_client.HttpClient()
        await client.open_session(connection_limit=10)
        session = client()
        # Use 'session' to make asynchronous HTTP requests
        await client.close_session()
    ```
"""
from typing import final

from aiohttp import ClientSession, ClientTimeout, TCPConnector

from base.base_class import BaseClass


@final
class HttpClient(BaseClass):
    """
    An asynchronous HTTP client using the aiohttp library.

    Inherits from BaseClass and is marked as final.
    """

    def __init__(self) -> None:
        """
        Initializes the HttpClient instance.
        """
        self._session: ClientSession | None
        super().__init__()

    async def close_session(self) -> None:
        """
        Closes the aiohttp client session if it's not None.
        """
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def open_session(
        self,
        connection_limit: int | None = None,
        timeout: int = 30
    ) -> None:
        """
        Opens a new aiohttp client session.

        Parameters:
        - connection_limit (Optional[int]): Limit the number of simultaneous
            connections.
        - timeout (int): Optional. The timeout value for the client session.

        Example:
        ```python
            await open_session(connection_limit=10, timeout=30)
        ```
        """
        _timeout: ClientTimeout = ClientTimeout(total=timeout)
        if connection_limit:
            connector: TCPConnector = TCPConnector(limit=connection_limit)
            self._session = ClientSession(
                connector=connector,
                timeout=_timeout
            )
        else:
            self._session = ClientSession(timeout=_timeout)

    def __call__(self) -> ClientSession:
        """
        Allows instances of HttpClient to be called like a function.

        Asserts that the _session is not None and returns the current
        ClientSession.

        Returns:
        ClientSession: The current aiohttp client session.

        Example:
        ```python
            client = HttpClient()
            session = client()
        ```
        """
        assert self._session is not None
        return self._session
