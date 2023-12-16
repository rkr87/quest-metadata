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
        # Use 'client' to make asynchronous HTTP requests
        await client.close_session()
    ```
"""

import socket
from asyncio.exceptions import TimeoutError as TOError
from http import HTTPStatus
from typing import final

from aiohttp import ClientResponse, ClientSession, ClientTimeout, TCPConnector

from base.base_class import BaseClass
from base.singleton import Singleton


@final
class HttpClient(BaseClass, metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]
    """
    An asynchronous HTTP client using the aiohttp library.
    Inherits from BaseClass and is marked as final.
    """

    def __init__(self) -> None:
        """
        Initializes the HttpClient.
        """
        self._session: ClientSession | None
        super().__init__()

    async def close_session(self) -> None:
        """
        Closes the existing client session.
        """
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def open_session(
        self,
        connection_limit: int = 100,
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
        connector = TCPConnector(
            limit=connection_limit,
            family=socket.AF_INET,
            verify_ssl=False
        )
        self._session = ClientSession(
            connector=connector,
            timeout=_timeout
        )

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None,
        data: str | None = None
    ) -> ClientResponse | None:
        """
        Performs an HTTP GET request.

        Parameters:
        - url (str): The URL for the GET request.
        - headers (Optional[dict[str, str]]): Optional headers for the request.
        - data (Optional[str]): Optional data to be sent with the request.

        Returns:
        - ClientResponse | None: The response from the server or None if an
            error occurs.
        """
        assert self._session is not None
        try:
            resp: ClientResponse = await self._session.get(
                url,
                headers=headers,
                data=data
            )
        except TOError:
            return None
        return self._validate(resp)

    async def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: str | None = None
    ) -> ClientResponse | None:
        """
        Performs an HTTP POST request.

        Parameters:
        - url (str): The URL for the POST request.
        - headers (Optional[dict[str, str]]): Optional headers for the request.
        - data (Optional[str]): Optional data to be sent with the request.

        Returns:
        - ClientResponse | None: The response from the server or None if an
            error occurs.
        """
        assert self._session is not None
        try:
            resp: ClientResponse = await self._session.post(
                url,
                headers=headers,
                data=data
            )
        except TOError:
            return None
        return self._validate(resp)

    @staticmethod
    def _validate(response: ClientResponse) -> ClientResponse | None:
        """
        Validates the HTTP response.

        Parameters:
        - response (ClientResponse): The response from the server.

        Returns:
        - ClientResponse | None: The validated response or None if the status
            code is not OK.
        """
        return response if response.status == HTTPStatus.OK else None
