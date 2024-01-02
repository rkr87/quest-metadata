"""
Module providing an HTTP client using aiohttp.

Classes:
- HttpClient: Singleton class for making HTTP requests.

"""
import socket
from asyncio.exceptions import TimeoutError as TOError
from http import HTTPStatus
from typing import final

from aiohttp import ClientResponse, ClientSession, ClientTimeout, TCPConnector

from base.classes import Singleton
from utils.error_manager import ErrorManager


@final
class HttpClient(Singleton):
    """
    Singleton class for making HTTP requests.

    Attributes:
    - _session (ClientSession | None): The aiohttp ClientSession instance.

    Methods:
    - close_session: Close the aiohttp ClientSession.
    - open_session: Open a new aiohttp ClientSession.
    - get: Perform an HTTP GET request.
    - post: Perform an HTTP POST request.
    - _validate: Validate the HTTP response.
    """

    def __init__(self) -> None:
        self._session: ClientSession | None
        super().__init__()

    async def close_session(self) -> None:
        """
        Close the aiohttp ClientSession.
        """
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def open_session(
        self,
        connection_limit: int = 50,
        timeout: int = 600
    ) -> None:
        """
        Open a new aiohttp ClientSession.

        Args:
        - connection_limit (int): Maximum number of connections.
        - timeout (int): Timeout duration in seconds.
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
        headers: dict[str, str] | None = None,
        data: str | None = None
    ) -> ClientResponse | None:
        """
        Perform an HTTP GET request.

        Args:
        - url (str): The URL to make the request to.
        - headers (dict[str, str] | None): Additional headers for the request.
        - data (str | None): Data to be sent with the request.

        Returns:
        - ClientResponse | None: The HTTP response, or None if an error
            occurred.
        """
        assert self._session is not None
        try:
            resp: ClientResponse = await self._session.get(
                url,
                headers=headers,
                data=data
            )
        except TOError as e:
            error: str = ErrorManager().capture(
                e,
                context="HTTP GET request timed out",
                error_info={
                    "url": url,
                    "headers": headers,
                    "payload": data
                }
            )
            self._logger.warning("%s", error)
            return None
        return self._validate(resp)

    async def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: str | None = None
    ) -> ClientResponse | None:
        """
        Perform an HTTP POST request.

        Args:
        - url (str): The URL to make the request to.
        - headers (dict[str, str] | None): Additional headers for the request.
        - data (str | None): Data to be sent with the request.

        Returns:
        - ClientResponse | None: The HTTP response, or None if an error
            occurred.
        """
        assert self._session is not None
        try:
            resp: ClientResponse = await self._session.post(
                url,
                headers=headers,
                data=data
            )
        except TOError as e:
            error: str = ErrorManager().capture(
                e,
                context="HTTP POST request timed out",
                error_info={
                    "url": url,
                    "headers": headers,
                    "payload": data
                }
            )
            self._logger.warning("%s", error)
            return None
        return self._validate(resp)

    @staticmethod
    def _validate(response: ClientResponse) -> ClientResponse | None:
        """
        Validate the HTTP response.

        Args:
        - response (ClientResponse): The HTTP response.

        Returns:
        - ClientResponse | None: The HTTP response, or None if validation
            fails.
        """
        return response if response.status == HTTPStatus.OK else None
